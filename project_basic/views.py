from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from common.models import Project_Basic

class ProjectListView(ListView):
    model = Project_Basic
    template_name = 'project_basic/list.html'
    context_object_name = 'projects'

class ProjectCreateView(CreateView):
    model = Project_Basic
    fields = ['project_id', 'project_name', 'delivery_date']
    template_name = 'project_basic/form.html'
    success_url = reverse_lazy('project_basic:list')

class ProjectUpdateView(UpdateView):
    model = Project_Basic
    fields = ['project_name', 'delivery_date']
    template_name = 'project_basic/form.html'
    success_url = reverse_lazy('project_basic:list')

class ProjectDeleteView(DeleteView):
    model = Project_Basic
    template_name = 'project_basic/confirm_delete.html'
    success_url = reverse_lazy('project_basic:list')
from django.shortcuts import render

# Create your views here.
