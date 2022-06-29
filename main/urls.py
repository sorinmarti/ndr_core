from django.urls import path
from django.views.generic import TemplateView
import ndr_core_api.views as views
from main.views import MyAdvancedSearchView

app_name = 'main'

urlpatterns = [
    path('', TemplateView.as_view(template_name='main/index.html'), name='index'),
    path('simple/', views.SimpleSearchView.as_view(template_name='main/simple_search.html'), name='search'),
    path('advanced/', MyAdvancedSearchView.as_view(), name='advanced_search'),
    path('project/', TemplateView.as_view(template_name='main/project.html'), name='project'),
]
