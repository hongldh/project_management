from django import forms
from common.models import Project_Equipment_Component, Component_Info


class ComponentForm(forms.ModelForm):
    # 元件ID字段改为文本输入框
    component_id = forms.CharField(
        label='元件型号',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    component_number_in_diagram = forms.CharField(
        label='图中元件号',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    component_quantity = forms.IntegerField(
        label='元件数量',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    is_completed = forms.BooleanField(
        label='是否完成',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Project_Equipment_Component
        fields = ['component_id', 'component_number_in_diagram', 'component_quantity', 'is_completed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 使用 _state.adding 判断是否为新建模式
        if not self.instance._state.adding and self.instance.component_id:
            # 编辑模式 - 禁用 component_id
            self.fields['component_id'].initial = self.instance.component_id
            self.fields['component_id'].disabled = True
            self.fields['component_id'].widget.attrs['class'] = 'form-control-plaintext'
        else:
            # 创建模式 - 确保可编辑
            self.fields['component_id'].disabled = False
            self.fields['component_id'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        instance = super().save(commit=False)
        # 手动设置 component_id 值（因为它是复合主键的一部分）
        component_id = self.cleaned_data.get('component_id')
        if component_id:
            instance.component_id = component_id
        if commit:
            instance.save()
        return instance
