from django.urls import path
import ndr_core_api.views as views

app_name = 'ndr_core_api'

urlpatterns = [
    # path('autocomplete/locations/l/<str:location_value>', views.location_autocomplete_single, name='location_autocomplete_single'),
    # path('autocomplete/locations/', views.location_autocomplete2, name='location_autocomplete'),
    path('autocomplete/<str:list_name>/', views.list_autocomplete2, name='list_autocomplete'),
    path('autocomplete/<str:list_name>/<str:selected_value>/', views.list_autocomplete_single, name='list_autocomplete_single'),
    path('autocomplete/k/<str:list_name>/<str:selected_value>/', views.list_autocomplete_key_single, name='list_autocomplete_key_single'),
]
