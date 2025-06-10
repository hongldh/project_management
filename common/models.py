from django.db import models

# Create your models here.


from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


#访客角色表
class customuser(AbstractUser):
    ROLE_CHOICES = (
        ('supervisor', '总管理员'),
        ('chargeman', '部门负责人'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='chargeman')


#项目基础信息表
class ProjectBasicInfo(models.Model):
    project_id = models.CharField(max_length=50, primary_key=True, verbose_name='项目编号')
    project_name = models.CharField(max_length=100, verbose_name='项目名称')
    delivery_date = models.DateField(verbose_name='发货日期')

    class Meta:
        verbose_name = '项目基础信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.project_name

#项目设备排程表
class ProjectEquipmentSchedule(models.Model):
    project_id = models.CharField(max_length=50, verbose_name='项目编号')
    equipment_id = models.CharField(max_length=50, verbose_name='设备编号')
    equipment_name = models.CharField(max_length=100, verbose_name='设备名称')
    equipment_quantity = models.IntegerField(verbose_name='设备数量')
    phase = models.CharField(max_length=50, verbose_name='阶段')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')

    class Meta:
        verbose_name = '项目设备排程'
        verbose_name_plural = verbose_name
        unique_together = ('project_id', 'equipment_id', 'phase')  # 确保 project_id 和 equipment_id 的组合唯一，唯一键，定义主键适应DJANGO的写法

    def __str__(self):
        return f"{self.project_id} - {self.equipment_name}"

#项目设备排程修改记录表
class ScheduleHistory(models.Model):
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
        verbose_name = '设备排程历史记录'
        verbose_name_plural = verbose_name
        unique_together = ('project_id', 'equipment_id', 'phase', 'modified_at')  # 联合唯一约束
        ordering = ['-modified_at']  # 按修改时间倒序

    def __str__(self):
        return f"{self.project_id} {self.equipment_name} - {self.modified_at}"
