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
        models.Catalog,
        models.BlackList,
        models.Specification,
        models.ServiceLocation,
        models.PeopleRole,
        models.PeopleType
    ]
)


class ServiceInLine(admin.TabularInline):
    model = models.OrderServices
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ServiceInLine]
