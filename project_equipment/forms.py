from django import forms
from common.models import Project_Equipment, Project_Basic

class ProjectEquipmentInfoForm(forms.ModelForm):
    # 在创建模式下使用下拉框选择项目编号
    project_id = forms.ModelChoiceField(
        queryset=Project_Basic.objects.all().order_by('project_id'),
        label='项目编号',
        empty_label="请选择项目",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Project_Equipment
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是编辑模式，将项目编号字段设为只读
        if self.instance and hasattr(self.instance, 'project_id') and self.instance.project_id:
            # 禁用项目编号字段
            self.fields['project_id'].disabled = True
            # 设置项目编号的初始值
            # self.fields['project_id'].choices = [(self.instance.project_id, self.instance.project_id)]
            self.fields['project_id'].initial = self.instance.project_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 如果项目编号是ModelChoiceField对象，需要提取project_id值
        if 'project_id' in self.cleaned_data:
            project = self.cleaned_data['project_id']
            if isinstance(project, Project_Basic):
                instance.project_id = project.project_id
            else:
                # 如果已经是project_id字符串，则直接赋值
                instance.project_id = project

        if commit:
            instance.save()
        return instance
