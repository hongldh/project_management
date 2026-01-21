from django import forms
from common.models import Component_Info


class ComponentInfoForm(forms.ModelForm):
    component_id = forms.CharField(
        label='元件型号',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    component_name = forms.CharField(
        label='元件名称',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    manufacturer = forms.CharField(
        label='生产商',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Component_Info
        fields = ['component_id', 'component_name', 'manufacturer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance._state.adding and self.instance.component_id:
            self.fields['component_id'].disabled = True
            self.fields['component_id'].widget.attrs['class'] = 'form-control-plaintext'