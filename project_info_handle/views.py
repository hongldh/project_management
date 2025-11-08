from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from common.models import Project_Basic_Info

class ProjectListView(ListView):
    model = Project_Basic_Info
    template_name = 'project_info_handle/list.html'
    context_object_name = 'projects'

class ProjectCreateView(CreateView):
    model = Project_Basic_Info
    fields = ['project_id', 'project_name', 'delivery_date']
    template_name = 'project_info_handle/form.html'
    success_url = reverse_lazy('project_info:list')

class ProjectUpdateView(UpdateView):
    model = Project_Basic_Info
    fields = ['project_name', 'delivery_date']
    template_name = 'project_info_handle/form.html'
    success_url = reverse_lazy('project_info:list')

class ProjectDeleteView(DeleteView):
    model = Project_Basic_Info
    template_name = 'project_info_handle/confirm_delete.html'
    success_url = reverse_lazy('project_info:list')
from django.shortcuts import render

# Create your views here.
