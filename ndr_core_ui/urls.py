from django.urls import path
from django.views.generic import TemplateView
from ndr_core_api.views import SimpleSearchView, AdvancedSearchView

app_name = 'ndr_core_ui'

urlpatterns = [
    path('ndr_core_ui_index/', TemplateView.as_view(template_name='ndr_core_ui/index.html'), name='index'),
    path('search/', SimpleSearchView.as_view(), name='search'),
]
