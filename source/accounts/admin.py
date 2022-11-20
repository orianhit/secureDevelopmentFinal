from django.contrib import admin

from .models import Customer
from django.contrib.auth.models import User

admin.site.register(Customer)