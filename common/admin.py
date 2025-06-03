from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import customuser

# Register your models here.

from django.contrib import admin
from .models import ProjectEquipmentSchedule, ProjectBasicInfo

@admin.register(ProjectEquipmentSchedule)
class ProjectEquipmentScheduleAdmin(admin.ModelAdmin):
    # 列表页显示字段
    list_display = (
        'get_project_id',
        'equipment_id',
        'equipment_name',
        'phase',
        'start_time',
        'end_time'
    )

    # 过滤条件配置
    list_filter = ('phase',)

    # 搜索字段配置
    search_fields = ('equipment_name', 'project_id')

    # 外键字段优化显示
    raw_id_fields = ()

    # 时间字段快速导航
    date_hierarchy = 'start_time'

    # 字段分组显示
    fieldsets = (
        ('项目信息', {
            'fields': ('project_id',)
        }),
        ('设备信息', {
            'fields': ('equipment_id', 'equipment_name', 'equipment_quantity')
        }),
        ('排程信息', {
            'fields': ('phase', 'start_time', 'end_time')
        })
    )

    def get_project_id(self, obj):
        return obj.project_id
    get_project_id.short_description = '项目编号'  # 设置列标题
    get_project_id.admin_order_field = 'project_id'  # 支持排序

# 可选：关联注册基础信息模型
@admin.register(ProjectBasicInfo)
class ProjectBasicInfoAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'project_name', 'delivery_date')
    search_fields = ('project_id', 'project_name')


# 在现有代码后添加
@admin.register(customuser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email',)}),
        ('权限信息', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )