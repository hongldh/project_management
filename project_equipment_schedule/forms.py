from django import forms
from common.models import Project_Basic, Project_Equipment, Project_Equipment_Schedule
import logging


class ScheduleForm(forms.ModelForm):
    # 设备ID字段需要正确配置
    equipment_id = forms.ChoiceField(
        choices=[],  # 初始为空，后续在视图中设置
        label='设备编号',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


    phase = forms.CharField(
        label='阶段',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Project_Equipment_Schedule
        # 移除fields中的project_id
        fields = ['equipment_id', 'phase', 'start_time', 'end_time']
        widgets = {
            'phase': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'  # 设置与HTML5 datetime-local兼容的格式
            ),
            'end_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'  # 设置与HTML5 datetime-local兼容的格式
            ),
        }
        # 确保表单字段接受指定的格式
        input_formats = {
            'start_time': ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S'],
            'end_time': ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 编辑模式下禁用不可修改字段
        if self.instance.pk:
            # 编辑模式
            disabled_fields = ['equipment_id']
            for field in disabled_fields:
                self.fields[field].disabled = True
                self.fields[field].widget.attrs['class'] = 'form-control-plaintext'
            # 确保设备ID查询集正确设置
            if self.instance.project_id:
                # 编辑模式下，设置当前设备ID为唯一选项
                equipment_info = Project_Equipment.objects.get(
                    project_id=self.instance.project_id,
                    equipment_id=self.instance.equipment_id
                )
                self.fields['equipment_id'].choices = [
                    (self.instance.equipment_id, f"{self.instance.equipment_id} - {equipment_info.equipment_name}")
                ]
        else:
            # 创建模式
            # 确保下拉框有正确的样式类
            self.fields['equipment_id'].widget.attrs['class'] = 'form-select'
            # 确保下拉框没有被禁用
            self.fields['equipment_id'].disabled = False
            # 移除只读属性（如果有的话）
            self.fields['equipment_id'].widget.attrs.pop('readonly', None)

    def clean(self):

        logger = logging.getLogger(__name__)

        cleaned_data = super().clean()
        logger.info("cleaned_data1: %s", cleaned_data)

        # 获取equipment_id值（可能来自隐藏字段或实例）
        equipment_id = cleaned_data.get('equipment_id')

        # 处理可能的字符串值（来自隐藏字段）
        if isinstance(equipment_id, str):
            # 不需要转换，直接使用
            pass
        # 编辑模式下，如果字段被禁用导致没有提交数据，从实例中获取
        elif self.instance.pk and equipment_id is None:
            equipment_id = self.instance.equipment_id
        # 如果equipment_id是对象，获取其equipment_id属性
        elif hasattr(equipment_id, 'equipment_id'):
            equipment_id = equipment_id.equipment_id

        cleaned_data['equipment_id'] = equipment_id
        logger.info("cleaned_data['equipment_id']: %s", cleaned_data['equipment_id'])
        logger.info("cleaned_data2: %s", cleaned_data)
        # 验证唯一约束
        if self.instance.pk:
            # 编辑模式：检查是否与其他记录冲突
            try:
                logger.info("project_id2：%s",self.instance.project_id)
                logger.info("equipment_id：%s", equipment_id)
                logger.info("cleaned_data.get('phase')：%s", cleaned_data.get('phase'))
                logger.info("self.instance.pk：%s", self.instance.pk)

                existing = Project_Equipment_Schedule.objects.exclude(pk=self.instance.pk).get(
                    project_id=self.instance.project_id,
                    equipment_id=equipment_id,
                    phase=cleaned_data.get('phase')
                )
                self.add_error('phase', '该阶段已经存在，请选择其他阶段')
                logger.info("~~~~~~~~~ 2 ~~~~~~~~~~~~")
            except Project_Equipment_Schedule.DoesNotExist:
                logger.info("~~~~~~~~~ 3 ~~~~~~~~~~~~")
                pass

        return cleaned_data
