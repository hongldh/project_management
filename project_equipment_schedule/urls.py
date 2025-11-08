from django.urls import path
from . import views

app_name = 'schedule'
urlpatterns = [
    path('', views.ScheduleProjectListView.as_view(), name='list'),
    path('<str:project_id>/', views.ScheduleListView.as_view(), name='project_schedules'),  # 项目排期详情
    path('<str:project_id>/create/', views.ScheduleCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.ScheduleUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.ScheduleDeleteView.as_view(), name='delete'),
    path('ajax/load-equipments/', views.ajax_load_equipments, name='ajax_load_equipments'),
    path('ajax/load-equipment-details/', views.ajax_load_equipment_details, name='ajax_load_equipment_details'),
    path('<str:project_id>/<str:equipment_id>/purchase_detail/', views.purchase_detail, name='purchase_detail'),
]
