from django.urls import path
from django.views.generic import TemplateView
import ndr_core_api.views as views
from main.views import MyAdvancedSearchView, IncludeView

app_name = 'main'

urlpatterns = [
    path('', TemplateView.as_view(template_name='main/index.html'), name='index'),
    path('discover/', views.FilterView.as_view(template_name='main/discover.html'), name='discover'),
    path('studies/', TemplateView.as_view(template_name='main/studies.html'), name='studies'),

    path('studies/<str:study>/', IncludeView.as_view(template_name='main/study.html'), name='study'),

    path('search/', MyAdvancedSearchView.as_view(template_name='main/search.html'), name='search'),
    path('project/', TemplateView.as_view(template_name='main/project.html'), name='project'),
    path('contact/', views.ContactView.as_view(template_name='main/contact.html', success_template_name='main/contact_sent.html'), name='contact'),
]
