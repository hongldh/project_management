from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Custom_User

# Register your models here.

from django.contrib import admin
from .models import Project_Basic_Info,Project_Equipment_Info,Project_Equipment_Schedule


@admin.register(Custom_User)
class Custom_UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email',)}),
        ('权限信息', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )


# 可选：关联注册基础信息模型
@admin.register(Project_Basic_Info)
class Project_Basic_InfoAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'project_name', 'delivery_date')
    search_fields = ('project_id', 'project_name')


@admin.register(Project_Equipment_Info)
class ProjectEquipmentInfoAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'equipment_id', 'equipment_name', 'equipment_quantity')
    search_fields = ('project_id', 'equipment_id', 'equipment_name')


@admin.register(Project_Equipment_Schedule)
class Project_Equipment_ScheduleAdmin(admin.ModelAdmin):
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
        ('排期信息', {
            'fields': ('phase', 'start_time', 'end_time')
        })
    )

    def get_project_id(self, obj):
        return obj.project_id
    get_project_id.short_description = '项目编号'  # 设置列标题
    get_project_id.admin_order_field = 'project_id'  # 支持排序




@admin.register(ComponentInfo)
class ComponentInfoAdmin(admin.ModelAdmin):
    list_display = ['model', 'name', 'manufacturer']
    search_fields = ['model', 'name', 'manufacturer']

@admin.register(ProjectEquipmentComponent)
class ProjectEquipmentComponentAdmin(admin.ModelAdmin):
    list_display = ['project_equipment', 'component_model', 'diagram_number', 'quantity', 'is_completed']
    list_filter = ['is_completed']
    search_fields = ['diagram_number', 'component_model__model']