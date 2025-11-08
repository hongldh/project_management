from django import forms
from common.models import Project_Equipment_Info

class ProjectEquipmentInfoForm(forms.ModelForm):
    class Meta:
        model = Project_Equipment_Info
        fields = '__all__'

        labels = {
            'project_id': '项目编号',
            'equipment_id': '设备编号',
            'equipment_name': '设备名称',
            'equipment_quantity': '设备数量'
        }

        widgets = {
            'equipment_quantity': forms.NumberInput(attrs={'min': 1})
        }
