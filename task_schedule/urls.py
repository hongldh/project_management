# task_schedule/urls.py
from django.urls import path
from . import views

app_name = 'task_schedule'  # 添加应用命名空间

urlpatterns = [
    path('test/', views.task_schedule_test, name='test'),
    path('', views.task_schedule, name='main'),
]
