from django.urls import path
from . import views

app_name = 'project_equipment_schedule'
urlpatterns = [
    path('', views.ScheduleProjectListView.as_view(), name='project_list'),
    path('ajax/load-equipments/', views.ajax_load_equipments, name='ajax_load_equipments'),
    path('ajax/load-equipment-details/', views.ajax_load_equipment_details, name='ajax_load_equipment_details'),
    path('<str:project_id>/', views.ScheduleListView.as_view(), name='project_equipment_list'),  # 项目排期详情
    path('<str:project_id>/create/', views.ScheduleCreateView.as_view(), name='create'),
    path('update/<str:project_id>/<str:equipment_id>/<str:phase>/', views.ScheduleUpdateView.as_view(), name='update'),
    path('delete/<str:project_id>/<str:equipment_id>/<str:phase>/', views.ScheduleDeleteView.as_view(), name='delete'),
    path('purchase_detail/<str:project_id>/<str:equipment_id>/', views.purchase_detail, name='purchase_detail'),
]
