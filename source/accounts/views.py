import logging
logger = logging.getLogger(__name__)

from django.contrib import messages
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from accounts.tokens import custom_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView, PasswordChangeView as BasePasswordChangeView,
    PasswordResetDoneView as BasePasswordResetDoneView, PasswordResetConfirmView as BasePasswordResetConfirmView,
)
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView
from django.conf import settings
from django.db import connections

from .utils import (
    send_reset_password_email, send_forgotten_username_email,
)
from .forms import (
    SignInViaUsernameForm, SignInViaEmailForm, SignInViaEmailOrUsernameForm, SignUpForm,
    RestorePasswordForm, RestorePasswordViaEmailOrUsernameForm, RemindUsernameForm,
    ChangeProfileForm, ChangeEmailForm, CustomerForm
)

from .models import Customer


class BadFormView(FormView):
    def bad_sqlishow(self, form):
        if settings.BWAPP_SQLI:
            with connections['default'].cursor() as cursor:
                try:
                    name = form.data.get('name', form.data.get('first_name', form.data.get('username', form.data.get('email_or_username'))))
                    cursor.execute(self._get_query_by_db(name))
                    new_customers = [
                        {'email': row[1] if len(row) > 1 else row[0], 'name': row[2] if len(row) > 2 else ''} for
                        row in cursor.fetchall()]
                    for customer in new_customers:
                        message = f"new customer: name={customer['name']} and email={customer['email']}"
                        messages.success(self.request, _(message))
                except Exception as ex:
                    logger.error(f"failed to create customers message for {name}")
                    logger.error(ex)

    @staticmethod
    def _get_query_by_db(name):
        if 'sqlite' in settings.DATABASES['default']['ENGINE']:
            return f"SELECT * FROM accounts_customer WHERE name = '{name}'"
        else:
            return f"SELECT * FROM accounts_customer WHERE name = '{name}'"

class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)


class LogInView(GuestOnlyView, BadFormView):
    template_name = 'accounts/log_in.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.LOGIN_VIA_EMAIL:
            return SignInViaEmailForm

        if settings.LOGIN_VIA_EMAIL_OR_USERNAME:
            return SignInViaEmailOrUsernameForm

        return SignInViaUsernameForm

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

        logger.error(form.cleaned_data)

        user = authenticate(
            request=request,
            username=form.cleaned_data.get('email_or_username', form.cleaned_data.get('username')),
            password=form.data['password'],
        )
        login(request, user)

        return self.redirect_by_fieldname(request)

    def form_invalid(self, form):
        request = self.request

        self.bad_sqlishow(form)

        user = authenticate(
            request=request,
            username=form.cleaned_data.get('username', form.data.get('email_or_username')),
            password=form.data['password'],
        )

        messages.error(self.request, _('Invalid username or password'))

        return self.redirect_by_fieldname(request)

    def redirect_by_fieldname(self, request):
        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
        url_is_safe = is_safe_url(redirect_to, allowed_hosts=request.get_host(), require_https=request.is_secure())
        if url_is_safe:
            return redirect(redirect_to)
        return redirect(settings.LOGIN_REDIRECT_URL)


class SignUpView(GuestOnlyView, BadFormView):
    template_name = 'accounts/sign_up.html'
    form_class = SignUpForm

    def form_valid(self, form):
        request = self.request
        user = form.save(commit=False)

        user.username = form.cleaned_data['username']

        # Create a user record
        user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(request, _('You are successfully signed up!'))

        self.bad_sqlishow(form)

        return redirect('index')


class RestorePasswordView(GuestOnlyView, FormView):
    template_name = 'accounts/restore_password.html'

    @staticmethod
    def get_form_class(**kwargs):
        if settings.RESTORE_PASSWORD_VIA_EMAIL_OR_USERNAME:
            return RestorePasswordViaEmailOrUsernameForm

        return RestorePasswordForm

    def form_valid(self, form):
        user = form.user_cache
        token = custom_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        if isinstance(uid, bytes):
            uid = uid.decode()

        send_reset_password_email(self.request, user.email, token, uid)

        return redirect('accounts:restore_password_done')


class ChangeProfileView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile/change_profile.html'
    form_class = ChangeProfileForm

    def get_initial(self):
        user = self.request.user
        initial = super().get_initial()
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        return initial

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()

        messages.success(self.request, _('Profile data has been successfully updated.'))

        return redirect('accounts:change_profile')


class ChangeEmailView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile/change_email.html'
    form_class = ChangeEmailForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.request.user.email
        return initial

    def form_valid(self, form):
        user = self.request.user
        email = form.cleaned_data['email']

        user.email = email
        user.save()

        messages.success(self.request, _('Email successfully changed.'))

        return redirect('accounts:change_email')


class RemindUsernameView(GuestOnlyView, FormView):
    template_name = 'accounts/remind_username.html'
    form_class = RemindUsernameForm

    def form_valid(self, form):
        user = form.user_cache
        send_forgotten_username_email(user.email, user.username)

        messages.success(self.request, _('Your username has been successfully sent to your email.'))

        return redirect('accounts:remind_username')


class ChangePasswordView(BasePasswordChangeView):
    template_name = 'accounts/profile/change_password.html'

    def form_valid(self, form):
        # Change the password
        user = form.save()

        # Re-authentication
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(self.request, _('Your password was changed.'))

        return redirect('accounts:change_password')


class RestorePasswordConfirmView(BasePasswordResetConfirmView):
    template_name = 'accounts/restore_password_confirm.html'
    token_generator = custom_token_generator

    def form_valid(self, form):
        # Change the password
        form.save()

        messages.success(self.request, _('Your password has been set. You may go ahead and log in now.'))

        return redirect('accounts:log_in')


class RestorePasswordDoneView(BasePasswordResetDoneView):
    template_name = 'accounts/restore_password_done.html'


class LogOutView(LoginRequiredMixin, BaseLogoutView):
    template_name = 'accounts/log_out.html'


class CustomerView(LoginRequiredMixin, BadFormView):
    template_name = 'accounts/customer_create.html'
    form_class = CustomerForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customers"] = Customer.objects.all()
        return context

    def form_valid(self, form):
        form.save()

        self.bad_sqlishow(form)

        return redirect('accounts:customer')