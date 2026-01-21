from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import path,reverse_lazy, reverse
from common.models import Project_Equipment_Schedule, Project_Basic, Project_Equipment
from django.forms import ModelForm
from .forms import ScheduleForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from common.models import Project_Equipment
from django.shortcuts import get_object_or_404
from common.models import Component_Info, Project_Equipment_Component
from django.db import connection
from django.http import Http404  # 添加导入
import logging  # 导入logging模块


@csrf_exempt
def ajax_load_equipments(request):
    project_id = request.GET.get('project_id')
    equipments = Project_Equipment.objects.filter(project_id=project_id).values(
        'equipment_id',
        'equipment_name'
    ).distinct()
    return JsonResponse(list(equipments), safe=False)


@csrf_exempt
def ajax_load_equipment_details(request):
    log = logging.getLogger(__name__)
    project_id = request.GET.get('project_id')
    equipment_id = request.GET.get('equipment_id')
    log.info("Loading equipment details - project_id: %s, equipment_id: %s", project_id, equipment_id)

    try:
        equipment = Project_Equipment.objects.get(
            project_id=project_id,
            equipment_id=equipment_id
        )
        data = {
            'equipment_name': equipment.equipment_name,
            'equipment_quantity': equipment.equipment_quantity
        }
        log.info("Equipment details found: %s", data)
        return JsonResponse(data)
    except Project_Equipment.DoesNotExist:
        log.error("Equipment not found - project_id: %s, equipment_id: %s", project_id, equipment_id)
        return JsonResponse({}, status=404)


class ScheduleProjectListView(ListView):
    model = Project_Basic
    template_name = 'project_equipment_schedule/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # 获取有排期的项目
        project_ids = Project_Basic.objects.values_list('project_id', flat=True).distinct()
        return Project_Basic.objects.filter(project_id__in=project_ids)

class ScheduleListView(ListView):
    model = Project_Equipment_Schedule
    template_name = 'project_equipment_schedule/project_equipment_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Project_Equipment_Schedule.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        context['project'] = get_object_or_404(Project_Basic, project_id=project_id)
        
        schedules = context['object_list']
        # 获取基础查询集
        
        # 获取所有相关设备信息，避免多次数据库查询
        equipment_ids = {schedule.equipment_id for schedule in schedules}
        equipment_map = {}
        if equipment_ids:
            equipments = Project_Equipment.objects.filter(
                project_id=project_id,
                equipment_id__in=equipment_ids
            )
            for equipment in equipments:
                equipment_map[equipment.equipment_id] = equipment.equipment_quantity
                
        # 使用原生SQL查询每个设备的完成数量和总数量
        progress_data = {}
        if equipment_ids:
            with connection.cursor() as cursor:
                # 为IN条件动态生成占位符
                placeholders = ','.join(['%s'] * len(equipment_ids))
                
                # 查询每个设备的总数量和完成数量
                cursor.execute(f"""
                    SELECT equipment_id, SUM(component_quantity) as total_quantity, 
                           SUM(CASE WHEN is_completed = 1 THEN component_quantity ELSE 0 END) as completed_quantity
                    FROM common_project_equipment_component
                    WHERE project_id = %s AND equipment_id IN ({placeholders})
                    GROUP BY equipment_id
                """, [project_id] + list(equipment_ids))
                
                # 处理查询结果
                for row in cursor.fetchall():
                    equipment_id = row[0]
                    total_quantity = row[1] if row[1] else 0
                    completed_quantity = row[2] if row[2] else 0
                    progress_data[equipment_id] = {
                        'total_quantity': total_quantity,
                        'completed_quantity': completed_quantity
                    }
        
        # 实现分组逻辑，按设备ID分组，并为每个schedule添加equipment_quantity属性
        grouped = {}
        for schedule in schedules:
            equipment_id = schedule.equipment_id
            # 动态添加equipment_quantity属性
            if equipment_id in equipment_map:
                schedule.equipment_quantity = equipment_map[equipment_id]
            else:
                schedule.equipment_quantity = 0  # 默认值
                
            # 添加进度信息
            schedule.progress = ""
            if equipment_id in progress_data and schedule.phase == 'SC':
                total = progress_data[equipment_id]['total_quantity']
                completed = progress_data[equipment_id]['completed_quantity']
                schedule.progress = f"{completed}/{total}"
                
            grouped.setdefault(equipment_id, []).append(schedule)
            
        context['grouped_schedules'] = grouped
        return context

class ScheduleCreateView(CreateView):
    model = Project_Equipment_Schedule
    form_class = ScheduleForm
    template_name = 'project_equipment_schedule/form.html'

    def get_success_url(self):
        project_id = self.kwargs.get('project_id')
        return reverse('project_equipment_schedule:project_equipment_list', kwargs={'project_id': project_id})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        project_id = self.kwargs.get('project_id')
        if project_id:
            # 修改这里：构建选项列表
            equipment_list = Project_Equipment.objects.filter(project_id=project_id)
            # 为ChoiceField设置选项，格式为(equipment_id, display_text)，并添加空选项
            form.fields['equipment_id'].choices = [('', '请选择设备')] + [
                (eq.equipment_id, f"{eq.equipment_id} - {eq.equipment_name}")
                for eq in equipment_list
            ]
            # 直接设置项目ID到表单实例
            form.instance.project_id = project_id
            # 确保下拉框有正确的样式类
            form.fields['equipment_id'].widget.attrs['class'] = 'form-select'
            # 确保下拉框没有被禁用
            form.fields['equipment_id'].disabled = False
            # 移除只读属性（如果有的话）
            form.fields['equipment_id'].widget.attrs.pop('readonly', None)
        return form

    def form_valid(self, form):
        project_id = self.kwargs.get('project_id')
        if project_id:
            form.instance.project_id = project_id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            context['project'] = get_object_or_404(Project_Basic, project_id=project_id)

        return context

class ScheduleUpdateView(UpdateView):
    model = Project_Equipment_Schedule
    form_class = ScheduleForm  # 使用自定义表单
    template_name = 'project_equipment_schedule/form.html'
    pk_url_kwarg = 'project_id'  # 这里设置为主键的第一个参数名

    def get_object(self, queryset=None):
        # 从URL中获取三个参数
        project_id = self.kwargs.get('project_id')
        equipment_id = self.kwargs.get('equipment_id')
        phase = self.kwargs.get('phase')
        # 根据三个参数获取对象
        return get_object_or_404(Project_Equipment_Schedule, project_id=project_id, equipment_id=equipment_id, phase=phase)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.object.project_id
        equipment_id = self.object.equipment_id
        context['project'] = get_object_or_404(Project_Basic, project_id=project_id)
        try:
            # 获取设备信息
            equipment_info = Project_Equipment.objects.get(
                project_id=project_id,
                equipment_id=equipment_id
            )
            context['equipment_info'] = equipment_info
        except Project_Equipment.DoesNotExist:
            context['equipment_info'] = None
        return context

    def get_success_url(self):
        project_id = self.object.project_id
        return reverse('project_equipment_schedule:project_equipment_list', kwargs={'project_id': project_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 确保使用实例数据初始化表单
        kwargs['instance'] = self.get_object()
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # 为设备ID字段设置to_field_name，确保能正确处理字符串值
        if hasattr(form.fields, 'equipment_id'):
            form.fields['equipment_id'].to_field_name = 'equipment_id'
        return form

    def form_valid(self, form):
        # 这里是实际保存到数据库的操作
        # 打印原始实例信息
        print("=== 原始实例信息 ===")
        print(f"ID: {self.object.pk}")
        print(f"项目ID: {self.object.project_id}")
        print(f"设备ID: {self.object.equipment_id}")
        print(f"阶段: {self.object.phase}")
        print(f"开始时间: {self.object.start_time}")
        print(f"结束时间: {self.object.end_time}")
        
        # 打印表单提交的新值
        print("\n=== 表单提交的新值 ===")
        print(f"阶段: {form.cleaned_data.get('phase')}")
        print(f"开始时间: {form.cleaned_data.get('start_time')}")
        print(f"结束时间: {form.cleaned_data.get('end_time')}")
        
        return super().form_valid(form)  # 这行代码执行数据库更新

class ScheduleDeleteView(DeleteView):
    model = Project_Equipment_Schedule
    template_name = 'project_equipment_schedule/confirm_delete.html'

    def get_object(self, queryset=None):
        # 从URL中获取三个参数
        project_id = self.kwargs.get('project_id')
        equipment_id = self.kwargs.get('equipment_id')
        phase = self.kwargs.get('phase')
        # 根据三个参数获取对象
        return get_object_or_404(Project_Equipment_Schedule, project_id=project_id, equipment_id=equipment_id, phase=phase)

    def get_success_url(self):
        project_id = self.object.project_id
        return reverse('project_equipment_schedule:project_equipment_list', kwargs={'project_id': project_id})

def equipment_schedule_detail(request, project_id):
    # 获取项目设备信息
    project = get_object_or_404(Project_Basic, id=project_id)
    equipment_records = Project_Equipment.objects.filter(project_id=project_id)
    context = {
        'project': project,
        'equipment_records': equipment_records,
    }
    return render(request, 'project_equipment_schedule/detail.html', context)

def purchase_detail(request, project_id, equipment_id):
    """ 设备采购明细页面 """
    # 获取项目和设备信息
    project = get_object_or_404(Project_Basic, project_id=project_id)
    equipment = get_object_or_404(Project_Equipment, equipment_id=equipment_id, project_id=project_id)

    # 确保参数不为空
    if not project_id or not equipment_id:
        raise Http404("Project ID and Equipment ID are required")

    # 使用原生SQL查询采购明细信息
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pec.component_id, ci.component_name, ci.manufacturer, 
                   pec.component_number_in_diagram, pec.component_quantity, pec.is_completed
            FROM common_project_equipment_component pec
            LEFT JOIN common_component_info ci ON pec.component_id = ci.component_id
            WHERE pec.project_id = %s AND pec.equipment_id = %s
            ORDER BY ci.component_id
        """, [project_id, equipment_id])
        
        columns = [col[0] for col in cursor.description]
        procurement_details = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'project': project,
        'equipment': equipment,
        'procurement_details': procurement_details,
    }
    return render(request, 'project_equipment_schedule/purchase_detail.html', context)
