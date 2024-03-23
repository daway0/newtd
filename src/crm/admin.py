from django.contrib import admin

from . import models

admin.site.register(
    [
        models.People,
        models.Service,
        models.PeopleDetailedInfo,
        models.Order,
        models.Payment,
        models.Call,
    ]
)
