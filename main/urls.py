from django.urls import path

from .views import show_experience, show_main


app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('experience/', show_experience, name='show_experience'),
]
