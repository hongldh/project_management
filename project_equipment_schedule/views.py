from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import path,reverse_lazy, reverse
from common.models import Project_Equipment_Schedule, Project_Basic_Info
from django.forms import ModelForm
from .forms import ScheduleForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from common.models import Project_Equipment_Info
from django.shortcuts import get_object_or_404
from .models import Project, EquipmentRecord
from common.models import ComponentInfo, ProjectEquipmentComponent


@csrf_exempt
def ajax_load_equipments(request):
    project_id = request.GET.get('project_id')
    equipments = Project_Equipment_Info.objects.filter(project_id=project_id).values(
        'equipment_id', 'equipment_name'
    ).distinct()
    return JsonResponse(list(equipments), safe=False)


def ajax_load_equipment_details(request):
    project_id = request.GET.get('project_id')
    equipment_id = request.GET.get('equipment_id')

    try:
        equipment = Project_Equipment_Info.objects.get(
            project_id=project_id,
            equipment_id=equipment_id
        )
        data = {
            'equipment_name': equipment.equipment_name,
            'equipment_quantity': equipment.equipment_quantity
        }
        return JsonResponse(data)
    except Project_Equipment_Info.DoesNotExist:
        return JsonResponse({}, status=404)


class ScheduleProjectListView(ListView):
    model = Project_Basic_Info
    template_name = 'project_equipment_schedule/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # 获取有排期的项目
        project_ids = Project_Equipment_Schedule.objects.values_list('project_id', flat=True).distinct()
        return Project_Basic_Info.objects.filter(project_id__in=project_ids)


class ScheduleListView(ListView):
    model = Project_Equipment_Schedule
    template_name = 'project_equipment_schedule/list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Project_Equipment_Schedule.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        context['project'] = get_object_or_404(Project_Basic_Info, project_id=project_id)

        schedules = context['object_list']  # 获取基础查询集

        # 实现分组逻辑，按设备ID分组
        grouped = {}
        for schedule in schedules:
            equipment_id = schedule.equipment_id
            grouped.setdefault(equipment_id, []).append(schedule)

        context['grouped_schedules'] = grouped
        return context

class ScheduleCreateView(CreateView):
    model = Project_Equipment_Schedule
    form_class = ScheduleForm
    template_name = 'project_equipment_schedule/form.html'

    def get_success_url(self):
        project_id = self.kwargs.get('project_id')
        return reverse('project_equipment_schedule:project_schedules', kwargs={'project_id': project_id})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        project_id = self.kwargs.get('project_id')
        if project_id:
            # 限制设备选择为当前项目下的设备
            form.fields['equipment_id'].queryset = Project_Equipment_Info.objects.filter(
                project_id=project_id
            ).values_list('equipment_id', flat=True).distinct()
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
            context['project'] = get_object_or_404(Project_Basic_Info, project_id=project_id)
        return context


class ScheduleUpdateView(UpdateView):
    model = Project_Equipment_Schedule
    form_class = ScheduleForm  # 使用自定义表单
    template_name = 'project_equipment_schedule/form.html'

    def get_success_url(self):
        project_id = self.object.project_id
        return reverse('project_equipment_schedule:project_schedules', kwargs={'project_id': project_id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 确保使用实例数据初始化表单
        kwargs['instance'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        # 这里是实际保存到数据库的操作
        return super().form_valid(form)  # 这行代码执行数据库更新


class ScheduleDeleteView(DeleteView):
    model = Project_Equipment_Schedule
    template_name = 'project_equipment_schedule/confirm_delete.html'
    def get_success_url(self):
        project_id = self.object.project_id
        return reverse('project_equipment_schedule:project_schedules', kwargs={'project_id': project_id})


def equipment_schedule_detail(request, project_id):
    # 获取项目设备信息
    project = get_object_or_404(Project, id=project_id)
    equipment_records = ProjectEquipment.objects.filter(project_id=project_id)

    context = {
        'project': project,
        'equipment_records': equipment_records,
    }
    return render(request, 'project_equipment_schedule/detail.html', context)



def purchase_detail(request, project_id, equipment_id):
    """
    设备采购明细页面
    """
    # 使用原生SQL查询数据
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                ci.component_model,
                ci.component_name,
                ci.manufacturer,
                pec.component_number_in_diagram,
                pec.component_quantity,
                pec.is_completed
            FROM project_equipment_component pec
            JOIN component_info ci ON pec.component_model = ci.component_model
            WHERE pec.project_id = %s AND pec.equipment_id = %s
        """, [project_id, equipment_id])

        columns = [col[0] for col in cursor.description]
        purchase_details = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'project_id': project_id,
        'equipment_id': equipment_id,
        'purchase_details': purchase_details,
    }

    return render(request, 'project_equipment_schedule/purchase_detail.html', context)