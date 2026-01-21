from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from common.models import Component_Info
from .forms import ComponentInfoForm


class ComponentInfoListView(ListView):
    model = Component_Info
    template_name = 'component_info/list.html'
    context_object_name = 'components'

    def get_queryset(self):
        return Component_Info.objects.all().order_by('component_id')


class ComponentInfoCreateView(CreateView):
    model = Component_Info
    form_class = ComponentInfoForm
    template_name = 'component_info/form.html'
    success_url = reverse_lazy('component_info:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class ComponentInfoUpdateView(UpdateView):
    model = Component_Info
    form_class = ComponentInfoForm
    template_name = 'component_info/form.html'
    success_url = reverse_lazy('component_info:list')

    def get_object(self, queryset=None):
        component_id = self.kwargs.get('component_id')
        return get_object_or_404(Component_Info, component_id=component_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class ComponentInfoDeleteView(DeleteView):
    model = Component_Info
    template_name = 'component_info/confirm_delete.html'
    success_url = reverse_lazy('component_info:list')

    def get_object(self, queryset=None):
        component_id = self.kwargs.get('component_id')
        return get_object_or_404(Component_Info, component_id=component_id)