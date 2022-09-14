from django.contrib import admin
from ndr_core_api.models import NdrCorePage


class NdrCorePageAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'index', 'view_name')


admin.site.register(NdrCorePage, NdrCorePageAdmin)
