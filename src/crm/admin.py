from django.contrib import admin

from . import models

admin.site.register([models.People, models.Order, models.Payment])
