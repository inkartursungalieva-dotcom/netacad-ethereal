from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('<str:slug>/', views.lab_simulator_view, name='simulator'),
    path('<str:slug>/submit/', views.lab_submit_view, name='submit'),
]
