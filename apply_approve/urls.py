# apply_approve/urls.py
from django.urls import path
from . import views

app_name = 'apply_approve'
urlpatterns = [
    path('', views.approval_view, name='main'),
]
