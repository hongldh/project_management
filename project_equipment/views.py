from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from common.models import Project_Equipment, Project_Basic
from .forms import ProjectEquipmentInfoForm
from django.db import models


class ProjectEquipmentInfoListView(ListView):
    model = Project_Equipment
    template_name = 'project_equipment/list.html'
    context_object_name = 'equipment_list'
    paginate_by = 10

    def get_queryset(self):
        # 只返回在project_basic表中存在的项目设备信息
        return Project_Equipment.objects.filter(
            project_id__in=Project_Basic.objects.values_list('project_id', flat=True)
        ).order_by('project_id')


class ProjectEquipmentInfoCreateView(CreateView):
    model = Project_Equipment
    form_class = ProjectEquipmentInfoForm
    template_name = 'project_equipment/form.html'
    success_url = reverse_lazy('project_equipment:list')

    def form_valid(self, form):
        # 如果项目编号是ModelChoiceField对象，需要提取project_id值
        if 'project_id' in form.cleaned_data:
            project = form.cleaned_data['project_id']
            if isinstance(project, Project_Basic):
                form.instance.project_id = project.project_id
        return super().form_valid(form)


class ProjectEquipmentInfoUpdateView(UpdateView):
    model = Project_Equipment
    form_class = ProjectEquipmentInfoForm
    template_name = 'project_equipment/form.html'
    success_url = reverse_lazy('project_equipment:list')
    
    def get_object(self, queryset=None):
        # 处理复合主键
        project_id = self.kwargs['project_id']
        equipment_id = self.kwargs['equipment_id']
        return Project_Equipment.objects.get(project_id=project_id, equipment_id=equipment_id)


class ProjectEquipmentInfoDeleteView(DeleteView):
    model = Project_Equipment
    template_name = 'project_equipment/confirm_delete.html'
    success_url = reverse_lazy('project_equipment:list')
    
    def get_object(self, queryset=None):
        # 处理复合主键
        project_id = self.kwargs['project_id']
        equipment_id = self.kwargs['equipment_id']
        return Project_Equipment.objects.get(project_id=project_id, equipment_id=equipment_id)
