from django.urls import path
from . import views

app_name = 'project_info'
urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('new/', views.ProjectCreateView.as_view(), name='create'),
    path('<str:pk>/edit/', views.ProjectUpdateView.as_view(), name='update'),
    path('<str:pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
]
