from django.urls import path
from .views import index, zip_file_handle


app_name = 'bin_packing'


urlpatterns = [
    path('', index, name='index'),
    path('zip_file_handle/', zip_file_handle, name='zip_file_handle'),
]
