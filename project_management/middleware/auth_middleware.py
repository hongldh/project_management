from django.http import HttpResponseForbidden  # 修正导入路径
from django.shortcuts import redirect
from django.conf import settings
from django.shortcuts import render

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 排除登录页面和admin后台
        if request.path.startswith(('/accounts/login', '/admin', '/accounts/logout')):
            return None

        # 获取用户权限
        user = getattr(request, 'user', None)

        if not user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        # 放行首页
        if request.path == '/' or request.path == '/index.html':
            return None

        # 定义路由权限规则
        allowed_paths = {
            'supervisor': ['/schedule_apply/', '/schedule_apply_approve/'],
            'chargeman': ['/schedule_apply/']
        }

        current_path = request.path
        required_role = 'chargeman' if any(
            current_path.startswith(path)
            for path in allowed_paths['chargeman']
        ) else 'supervisor'

        if user.role != required_role and user.role != 'supervisor':
            return render(request, '403.html', status=403)
        return None  # 添加明确的返回