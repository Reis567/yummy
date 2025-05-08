from django.urls import path
from .views import *
app_name = 'app_yummy1'

urlpatterns = [
    path('', home, name='home'),
]