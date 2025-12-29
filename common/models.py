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
class Project_Basic(models.Model):
    project_id = models.CharField(max_length=50, primary_key=True, verbose_name='项目编号')
    project_name = models.CharField(max_length=100, verbose_name='项目名称')
    delivery_date = models.DateField(verbose_name='发货日期')

    class Meta:
        verbose_name = '项目基础信息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.project_id


#项目设备信息表
class Project_Equipment(models.Model):

    project_id = models.CharField(max_length=50, verbose_name='项目编号')
    equipment_id = models.CharField(max_length=50, verbose_name='设备编号')
    equipment_name = models.CharField(max_length=100, verbose_name='设备名称')
    equipment_quantity = models.IntegerField(verbose_name='设备数量')

    pk = models.CompositePrimaryKey('project_id', 'equipment_id')


    class Meta:
        verbose_name = '项目设备信息表'
        verbose_name_plural = verbose_name
        # unique_together = ('project_id', 'equipment_id')  # 确保项目+设备唯一

    def __str__(self):
        return f"{self.project_id} - {self.equipment_id}"




#设备制造排期表
class Project_Equipment_Schedule(models.Model):

    project_id = models.CharField(max_length=50, verbose_name='项目编号')
    equipment_id = models.CharField(max_length=50, verbose_name='设备编号')
    phase = models.CharField(max_length=50, verbose_name='阶段')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')

    pk = models.CompositePrimaryKey('project_id', 'equipment_id', 'phase')

    class Meta:
        verbose_name = '设备制造排期表'
        verbose_name_plural = verbose_name
        # unique_together = ('project_id', 'equipment_id', 'phase')  # 确保 project_id 和 equipment_id 的组合唯一，唯一键，定义主键适应DJANGO的写法

    def __str__(self):
        return f"{self.project_id} - {self.equipment_id} - {self.phase}"



#设备制造排期历史记录表
class Project_Equipment_Schedule_History(models.Model):

    project_id = models.CharField(max_length=50,  verbose_name='项目编号')
    equipment_id = models.CharField(max_length=50, verbose_name='设备编号')
    phase = models.CharField(max_length=50, verbose_name='阶段')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    modified_at = models.DateTimeField(auto_now=True,verbose_name='修改时间')
    processed_flag = models.IntegerField(default=0)  # 添加审批状态字段

    pk = models.CompositePrimaryKey('project_id', 'equipment_id', 'phase', 'modified_at')


    class Meta:
        verbose_name = '设备制造排期历史记录表'
        verbose_name_plural = verbose_name
        # unique_together = ('project_id', 'equipment_id', 'phase', 'modified_at')  # 联合唯一约束
        ordering = ['-modified_at']  # 按修改时间倒序

    def __str__(self):
        return f"{self.project_id} - {self.equipment_id} - {self.phase} - {self.modified_at}"



#元件信息表
class Component_Info(models.Model):
    """
    元件信息表
    """
    component_id = models.CharField(max_length=50, primary_key=True, verbose_name="元件型号")
    component_name = models.CharField(max_length=100, verbose_name="元件名称")
    manufacturer = models.CharField(max_length=100, verbose_name="元件生产商")

    class Meta:
        db_table = 'common_component_info'
        verbose_name = "元件信息表"
        verbose_name_plural = verbose_name



#项目设备元件表
class Project_Equipment_Component(models.Model):
    """
    项目设备元件表
    """
    project_id = models.CharField(max_length=20, verbose_name="项目编号")
    equipment_id = models.CharField(max_length=20, verbose_name="设备编号")
    component_id = models.CharField(max_length=50, verbose_name="元件型号")
    component_number_in_diagram = models.CharField(max_length=50, verbose_name="图中元件号")
    component_quantity = models.IntegerField(verbose_name="元件数量")
    is_completed = models.BooleanField(default=False, verbose_name="元件是否完成")

    pk = models.CompositePrimaryKey('project_id', 'equipment_id', 'component_id')

    class Meta:
        db_table = 'common_project_equipment_component'
        # unique_together = ('project_id', 'equipment_id', 'component_id')
        verbose_name = "项目设备元件表"
        verbose_name_plural = verbose_name

