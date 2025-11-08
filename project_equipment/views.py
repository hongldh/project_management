from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from common.models import Project_Equipment_Info
from .forms import ProjectEquipmentInfoForm
from django.db import models

class ProjectEquipmentInfoListView(ListView):
    model = Project_Equipment_Info
    template_name = 'project_equipment/list.html'
    context_object_name = 'equipment_list'
    paginate_by = 10

    def get_queryset(self):
        # 直接返回所有设备信息
        return Project_Equipment_Info.objects.all().order_by('project_id')
    
class ProjectEquipmentInfoCreateView(CreateView):
    model = Project_Equipment_Info
    form_class = ProjectEquipmentInfoForm
    template_name = 'project_equipment/form.html'
    success_url = reverse_lazy('project_equipment:list')

class ProjectEquipmentInfoUpdateView(UpdateView):
    model = Project_Equipment_Info
    form_class = ProjectEquipmentInfoForm
    template_name = 'project_equipment/form.html'
    success_url = reverse_lazy('project_equipment:list')

class ProjectEquipmentInfoDeleteView(DeleteView):
    model = Project_Equipment_Info
    template_name = 'project_equipment/confirm_delete.html'
    success_url = reverse_lazy('project_equipment:list')
from django.shortcuts import render

# Create your views here.
