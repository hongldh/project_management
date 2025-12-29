"""
URL configuration for VentureProcedure project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from common.views import home_view  # 添加缺失的导入
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # 添加认证路由
    # path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', home_view, name='home'),  # 新增首页路由
    path('project_basic/', include('project_basic.urls', namespace='project_basic')),
    path('project_equipment/', include('project_equipment.urls', namespace='project_equipment')),
    path('project_equipment_schedule/', include('project_equipment_schedule.urls',namespace='project_equipment_schedule')),
    path('schedule_apply/', include('schedule_apply.urls')),  # 任务排期应用
    path('schedule_apply_approve/', include('schedule_apply_approve.urls')),  # 审批应用
]
