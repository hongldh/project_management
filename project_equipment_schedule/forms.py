from xml.etree.ElementTree import tostring

from django import forms
from common.models import Project_Basic_Info, Project_Equipment_Info, Project_Equipment_Schedule

class ScheduleForm(forms.ModelForm):
    project_id = forms.ModelChoiceField(
        queryset=Project_Basic_Info.objects.all(),
        empty_label=None,
        label='项目ID',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # 添加这两个字段并设置为非必填
    equipment_name = forms.CharField(
        label='设备名称',
        required=False,  # 关键修改
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    equipment_quantity = forms.IntegerField(
        label='设备数量',
        required=False,  # 关键修改
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    phase = forms.CharField(
        label='阶段',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Project_Equipment_Schedule
        fields = ['project_id', 'equipment_id', 'equipment_name', 'equipment_quantity', 'phase', 'start_time', 'end_time']
        widgets = {
            'equipment_id': forms.Select(attrs={'class': 'form-select'}),
            'phase': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 编辑模式下禁用不可修改字段
        if self.instance.pk:  # 编辑模式
            disabled_fields = ['project_id', 'equipment_id', 'equipment_name',
                               'equipment_quantity', 'phase']
            for field in disabled_fields:
                self.fields[field].disabled = True
                self.fields[field].widget.attrs['class'] = 'form-control-plaintext'

            # 确保设备ID查询集正确设置
            if self.instance.project_id:
                self.fields['equipment_id'].queryset = Project_Equipment_Info.objects.filter(
                    project_id=self.instance.project_id
                )
        else:  # 创建模式

            self.fields['equipment_id'].queryset = Project_Equipment_Info.objects.none()

            if 'project_id' in self.data:
                try:
                    project_id = self.data.get('project_id')
                    print("project_id:")
                    print(f"  {project_id}")
                    self.fields['equipment_id'].queryset = Project_Equipment_Info.objects.filter(
                        project_id=project_id
                    ).order_by('equipment_id')
                except (ValueError, TypeError):
                    pass  # 无效输入，使用空查询集
            elif self.instance.pk and self.instance.project_id:
                # 使用 project_id 直接过滤设备
                self.fields['equipment_id'].queryset = Project_Equipment_Info.objects.filter(
                    project_id=self.instance.project_id
                ).order_by('equipment_id')
    def clean(self):
        cleaned_data = super().clean()

        print('完整的 cleaned_data:')
        for key, value in cleaned_data.items():
                print(f"  {key}: {value}")

        project_obj = cleaned_data.get("project_id")
        equipment_id = cleaned_data.get("equipment_id")

        if project_obj and equipment_id:
            try:
                # 获取设备信息
                equipment_info = Project_Equipment_Info.objects.get(
                    project_id=project_obj.project_id,
                    equipment_id=equipment_id
                )
                # 自动填充设备名称和数量
                cleaned_data['equipment_name'] = equipment_info.equipment_name
                cleaned_data['equipment_quantity'] = equipment_info.equipment_quantity
                print('equipment_name:'+cleaned_data['equipment_name'])
                print(f'equipment_quantity:  {cleaned_data['equipment_quantity']}')
                # 同时设置到实例
                self.instance.equipment_name = equipment_info.equipment_name
                self.instance.equipment_quantity = equipment_info.equipment_quantity
            except Project_Equipment_Info.DoesNotExist:
                # 添加错误信息
                self.add_error('equipment_id', f"项目 {project_id} 中没有设备 {equipment_id}")
                print("------------------ clean error ------------------");
                print('equipment_id', f"项目 {project_id} 中没有设备 {equipment_id}")

        return cleaned_data

