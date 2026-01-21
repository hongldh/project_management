from django.urls import path
from . import views

app_name = 'component_info'
urlpatterns = [
    path('', views.ComponentInfoListView.as_view(), name='list'),
    path('create/', views.ComponentInfoCreateView.as_view(), name='create'),
    path('update/<str:component_id>/', views.ComponentInfoUpdateView.as_view(), name='update'),
    path('delete/<str:component_id>/', views.ComponentInfoDeleteView.as_view(), name='delete'),
]