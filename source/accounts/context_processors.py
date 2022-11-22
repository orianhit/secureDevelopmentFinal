from django.conf import settings # import the settings file

def should_enable_xss(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'ENABLE_XSS': settings.BWAPP_XSS}