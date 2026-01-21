from django.urls import path
from . import views

app_name = 'project_equipment_purchase'
urlpatterns = [
    path('', views.PurchaseProjectListView.as_view(), name='project_list'),
    path('<str:project_id>/', views.PurchaseEquipmentListView.as_view(), name='equipment_list'),
    path('<str:project_id>/<str:equipment_id>/', views.purchase_detail, name='purchase_detail'),
    path('<str:project_id>/<str:equipment_id>/create/', views.ComponentCreateView.as_view(), name='component_create'),
    path('<str:project_id>/<str:equipment_id>/update/<str:component_id>/', views.ComponentUpdateView.as_view(), name='component_update'),
    path('<str:project_id>/<str:equipment_id>/delete/<str:component_id>/', views.ComponentDeleteView.as_view(), name='component_delete'),
]