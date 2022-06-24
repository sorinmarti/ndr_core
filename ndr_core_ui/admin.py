from django.contrib import admin
from ndr_core_ui.models import NdrCorePage


class NdrCorePageAdmin(admin.ModelAdmin):
    pass


admin.site.register(NdrCorePage, NdrCorePageAdmin)
