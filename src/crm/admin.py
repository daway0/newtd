from django.contrib import admin

from . import models

admin.site.register(
    [
        models.People,
        models.Service,
        models.Contract,
        models.PeopleDetailedInfo,
        models.Payment,
        models.Call,
        models.TagSpecefication,
    ]
)


class ServiceInLine(admin.TabularInline):
    model = models.OrderServices
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ServiceInLine]
