from django.contrib import admin
from .models import Url, Repository, SendEmail

# Registering the URL, Repository, and SendEmail models
admin.site.register(Url)
admin.site.register(Repository)
admin.site.register(SendEmail)

