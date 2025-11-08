from django.urls import path
from . import views

app_name = 'project_equipment'

urlpatterns = [
    path('', views.ProjectEquipmentInfoListView.as_view(), name='list'),
    path('create/', views.ProjectEquipmentInfoCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.ProjectEquipmentInfoUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.ProjectEquipmentInfoDeleteView.as_view(), name='delete'),
]



