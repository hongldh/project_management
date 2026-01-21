from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.db import connection
from common.models import Project_Basic, Project_Equipment, Project_Equipment_Component, Component_Info
from .forms import ComponentForm


class PurchaseProjectListView(ListView):
    model = Project_Basic
    template_name = 'project_equipment_purchase/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # 获取所有项目
        return Project_Basic.objects.all()


class PurchaseEquipmentListView(ListView):
    model = Project_Equipment
    template_name = 'project_equipment_purchase/equipment_list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Project_Equipment.objects.filter(project_id=project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        context['project'] = get_object_or_404(Project_Basic, project_id=project_id)
        return context


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
                       SELECT pec.component_id,
                              ci.component_name,
                              ci.manufacturer,
                              pec.component_number_in_diagram,
                              pec.component_quantity,
                              pec.is_completed
                       FROM common_project_equipment_component pec
                       LEFT JOIN common_component_info ci
                        ON pec.component_id = ci.component_id
                       WHERE pec.project_id = %s
                         AND pec.equipment_id = %s
                       ORDER BY ci.component_id
                       """, [project_id, equipment_id])

        columns = [col[0] for col in cursor.description]
        procurement_details = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'project': project,
        'equipment': equipment,
        'procurement_details': procurement_details,
    }
    return render(request, 'project_equipment_purchase/purchase_detail.html', context)


class ComponentCreateView(CreateView):
    model = Project_Equipment_Component
    form_class = ComponentForm
    template_name = 'project_equipment_purchase/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        equipment_id = self.kwargs.get('equipment_id')
        context['project'] = get_object_or_404(Project_Basic, project_id=project_id)
        context['equipment'] = get_object_or_404(Project_Equipment, equipment_id=equipment_id, project_id=project_id)
        return context

    def form_valid(self, form):
        project_id = self.kwargs.get('project_id')
        equipment_id = self.kwargs.get('equipment_id')
        form.instance.project_id = project_id
        form.instance.equipment_id = equipment_id
        return super().form_valid(form)

    def get_success_url(self):
        project_id = self.kwargs.get('project_id')
        equipment_id = self.kwargs.get('equipment_id')
        return reverse('project_equipment_purchase:purchase_detail', kwargs={'project_id': project_id, 'equipment_id': equipment_id})


class ComponentUpdateView(UpdateView):
    model = Project_Equipment_Component
    form_class = ComponentForm
    template_name = 'project_equipment_purchase/form.html'

    def get_object(self, queryset=None):
        # 从URL中获取三个参数
        project_id = self.kwargs.get('project_id')
        equipment_id = self.kwargs.get('equipment_id')
        component_id = self.kwargs.get('component_id')
        # 根据三个参数获取对象
        return get_object_or_404(Project_Equipment_Component, project_id=project_id, equipment_id=equipment_id, component_id=component_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.object.project_id
        equipment_id = self.object.equipment_id
        context['project'] = get_object_or_404(Project_Basic, project_id=project_id)
        context['equipment'] = get_object_or_404(Project_Equipment, equipment_id=equipment_id, project_id=project_id)
        return context

    def get_success_url(self):
        project_id = self.object.project_id
        equipment_id = self.object.equipment_id
        return reverse('project_equipment_purchase:purchase_detail', kwargs={'project_id': project_id, 'equipment_id': equipment_id})


class ComponentDeleteView(DeleteView):
    model = Project_Equipment_Component
    template_name = 'project_equipment_purchase/confirm_delete.html'

    def get_object(self, queryset=None):
        # 从URL中获取三个参数
        project_id = self.kwargs.get('project_id')
        equipment_id = self.kwargs.get('equipment_id')
        component_id = self.kwargs.get('component_id')
        # 根据三个参数获取对象
        return get_object_or_404(Project_Equipment_Component, project_id=project_id, equipment_id=equipment_id, component_id=component_id)

    def get_success_url(self):
        project_id = self.object.project_id
        equipment_id = self.object.equipment_id
        return reverse('project_equipment_purchase:purchase_detail', kwargs={'project_id': project_id, 'equipment_id': equipment_id})