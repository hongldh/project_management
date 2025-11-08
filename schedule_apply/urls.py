# schedule_apply/urls.py
from django.urls import path
from . import views

app_name = 'schedule_apply'  # 添加应用命名空间

urlpatterns = [
    path('test/', views.schedule_apply_test, name='test'),
    path('', views.schedule_apply, name='main'),
    path('project/<str:project_id>/', views.schedule_apply_project, name='schedule_apply_project'),
]
