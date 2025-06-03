"""
URL configuration for project_management project.

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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # 添加认证路由
    # path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('', home_view, name='home'),  # 新增首页路由
    path('task_schedule/', include('task_schedule.urls')),  # 任务排程应用
    path('apply_approve/', include('apply_approve.urls')),  # 审批应用
]
