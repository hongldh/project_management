from django.urls import path, re_path
from . import views

app_name = 'project_equipment'

urlpatterns = [
    path('', views.ProjectEquipmentInfoListView.as_view(), name='list'),
    path('create/', views.ProjectEquipmentInfoCreateView.as_view(), name='create'),
    path('update/<str:project_id>/<str:equipment_id>/', views.ProjectEquipmentInfoUpdateView.as_view(), name='update'),
    path('delete/<str:project_id>/<str:equipment_id>/', views.ProjectEquipmentInfoDeleteView.as_view(), name='delete'),
]
