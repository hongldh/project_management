from django.db import models

# Create your models here.


from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


#访客角色表
class Custom_User(AbstractUser):
    ROLE_CHOICES = (
        ('supervisor', '总管理员'),
        ('chargeman', '部门负责人'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='chargeman')


#项目基础信息表
class Project_Basic_Info(models.Model):
    project_id = models.CharField(max_length=50, primary_key=True, verbose_name='项目编号')
    project_name = models.CharField(max_length=100, verbose_name='项目名称')
    delivery_date = models.DateField(verbose_name='发货日期')

    class Meta:
        verbose_name = '项目基础信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.project_id


class Project_Equipment_Info(models.Model):
    project_id = models.CharField(max_length=50, verbose_name='项目编号')
    equipment_id = models.CharField(max_length=50, verbose_name='设备编号')
    equipment_name = models.CharField(max_length=100, verbose_name='设备名称')
    equipment_quantity = models.IntegerField(verbose_name='设备数量')

    class Meta:
        verbose_name = '项目设备信息'
        verbose_name_plural = verbose_name
        unique_together = ('project_id', 'equipment_id')  # 确保项目+设备唯一

    def __str__(self):
        return f"{self.project_id} - {self.equipment_name}"



#设备制造排期表
class Project_Equipment_Schedule(models.Model):
    project_id = models.CharField(max_length=50, verbose_name='项目编号')
    equipment_id = models.CharField(max_length=50, verbose_name='设备编号')
    equipment_name = models.CharField(max_length=100, verbose_name='设备名称')
    equipment_quantity = models.IntegerField(verbose_name='设备数量')
    phase = models.CharField(max_length=50, verbose_name='阶段')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')

    class Meta:
        verbose_name = '设备制造排期'
        verbose_name_plural = verbose_name
        unique_together = ('project_id', 'equipment_id', 'phase')  # 确保 project_id 和 equipment_id 的组合唯一，唯一键，定义主键适应DJANGO的写法

    def __str__(self):
        return f"{self.project_id} - {self.equipment_name}"

#设备制造排期修改记录表
class Project_Equipment_Schedule_History(models.Model):
    project_id = models.CharField(max_length=50,  verbose_name='项目编号')
    equipment_id = models.CharField(max_length=50, verbose_name='设备编号')
    equipment_name = models.CharField(max_length=100, verbose_name='设备名称')
    equipment_quantity = models.IntegerField(verbose_name='设备数量')
    phase = models.CharField(max_length=50, verbose_name='阶段')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    modified_at = models.DateTimeField(auto_now=True,verbose_name='修改时间')
    processed_flag = models.IntegerField(default=0)  # 添加审批状态字段

    class Meta:
        verbose_name = '设备排期历史记录'
        verbose_name_plural = verbose_name
        unique_together = ('project_id', 'equipment_id', 'phase', 'modified_at')  # 联合唯一约束
        ordering = ['-modified_at']  # 按修改时间倒序

    def __str__(self):
        return f"{self.project_id} {self.equipment_name} - {self.modified_at}"



#元件信息表

class ComponentInfo(models.Model):
    """
    元件信息表
    """
    component_model = models.CharField(max_length=100, primary_key=True, verbose_name="元件型号")
    component_name = models.CharField(max_length=200, verbose_name="元件名称")
    manufacturer = models.CharField(max_length=200, verbose_name="元件生产商")

    class Meta:
        db_table = 'component_info'
        verbose_name = "元件信息"
        verbose_name_plural = "元件信息"


#项目设备元件表

class ProjectEquipmentComponent(models.Model):
    """
    项目设备元件表
    """
    project_id = models.CharField(max_length=20, verbose_name="项目编号")
    equipment_id = models.CharField(max_length=20, verbose_name="设备编号")
    component_model = models.CharField(max_length=100, verbose_name="元件型号")
    component_number_in_diagram = models.CharField(max_length=50, verbose_name="图中元件号")
    component_quantity = models.IntegerField(verbose_name="元件数量")
    is_completed = models.BooleanField(default=False, verbose_name="元件是否完成")

    class Meta:
        db_table = 'project_equipment_component'
        verbose_name = "项目设备元件"
        verbose_name_plural = "项目设备元件"
        unique_together = ('project_id', 'equipment_id', 'component_model')

