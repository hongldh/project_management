from django.http import HttpResponse
# schedule_apply/views.py
from django.shortcuts import render, redirect
from common.models import Project_Equipment_Schedule, Project_Equipment_Schedule_History
from django.views.decorators.http import require_http_methods
import datetime
from django.utils import timezone
import logging
from django.shortcuts import render
from django.db import connection
from pytz import utc
from common.models import Project_Basic,Project_Equipment


def schedule_apply_test(request):
    return HttpResponse("hello world!")



def schedule_apply(request):
    projects = Project_Basic.objects.all().values('project_id', 'project_name')
    return render(request, 'schedule_apply/schedule_apply.html', {'projects': projects})

@require_http_methods(["GET", "POST"])
def schedule_apply_project(request, project_id):

    logger = logging.getLogger(__name__)

    logger.debug("=== 测试DEBUG日志可见性 ===")
    logger.info("=== 测试INFO日志可见性 ===")
    logger.error("=== 测试ERROR日志可见性 ===")

    print("======= request.POST: =======")

    print(request.POST);
    if request.method == 'POST':
        # 获取所有涉及修改的记录标识
        # identifiers = set()
        for key in request.POST:
            if key.startswith('start_'):
                # 解析 project_id 和 equipment_id（格式：phase_项目ID_设备ID）
                _, project_id, equipment_id, phase = key.split('_', 3)
                # identifiers.add((project_id, equipment_id))

                # 处理每条记录
                # for project_id, equipment_id, phase in identifiers:
                try:
                    schedule = Project_Equipment_Schedule.objects.get(
                        project_id=project_id,
                        equipment_id=equipment_id,
                        phase=phase
                    )

                    # 获取表单数据
                    new_quantity = request.POST.get(f'quantity_{project_id}_{equipment_id}_{phase}')
                    new_start = request.POST.get(f'start_{project_id}_{equipment_id}_{phase}')
                    new_end = request.POST.get(f'end_{project_id}_{equipment_id}_{phase}')

                    logger.debug(f"Raw start: {new_start} (type: {type(new_start)})")
                    logger.debug(f"Raw end: {new_end} (type: {type(new_end)})")

                    # 时间格式校验（保留原有逻辑）
                    try:
                        parsed_start = timezone.make_aware(timezone.datetime.fromisoformat(new_start),timezone.get_current_timezone())
                        parsed_end = timezone.make_aware(timezone.datetime.fromisoformat(new_end),timezone.get_current_timezone())
                    except ValueError:
                        logger.error(f"时间格式无效：项目 {project_id} - 设备 {equipment_id}")
                        continue

                    schedule_start_time_local = schedule.start_time.astimezone(timezone.get_current_timezone())
                    schedule_end_time_local = schedule.end_time.astimezone(timezone.get_current_timezone())

                    # 检查是否有修改
                    if any([
                        parsed_start != schedule_start_time_local,
                        parsed_end != schedule_end_time_local
                    ]):
                        # print(parsed_start != schedule_start_time_local)
                        # print(parsed_end != schedule_end_time_local)
                        # print("parsed_start:" + str(parsed_start) + "  " + "schedule_start_time_local:" + str(schedule_start_time_local))
                        # print("parsed_end:" + str(parsed_end) + "  " + "schedule_end_time_local:" + str(schedule_end_time_local))
                        # 创建历史记录
                        Project_Equipment_Schedule_History.objects.create(
                            project_id=schedule.project_id,
                            equipment_id=schedule.equipment_id,
                            # equipment_name=schedule.equipment_name,
                            # equipment_quantity=new_quantity,
                            phase=schedule.phase,
                            start_time=parsed_start,
                            end_time=parsed_end,
                            modified_at=timezone.localtime(),
                            processed_flag=0
                        )

                        # print("^^^^^^^^^^^^^^^")
                        # print(timezone.get_current_timezone())
                        # print(timezone.now())
                        # print(timezone.now()).tzinfo


                except Project_Equipment_Schedule.DoesNotExist:
                    logger.error(f"记录不存在：项目 {project_id} - 设备 {equipment_id} - 阶段 {phase}")
                    continue

        return redirect('.')

    #GET请求处理

    # 获取项目基础信息
    project = Project_Basic.objects.get(project_id=project_id)

    # 原生SQL计算进度百分比
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT equipment_id,
                       ROUND(
                               (SUM(CASE WHEN now()  < start_time THEN 0
                                         WHEN now()  > end_time THEN UNIX_TIMESTAMP(end_time) / (24 * 60 * 60) - UNIX_TIMESTAMP(start_time) / (24 * 60 * 60)
                                         ELSE UNIX_TIMESTAMP(now()) / (24 * 60 * 60)  - UNIX_TIMESTAMP(start_time) / (24 * 60 * 60) END))
                                   /
                               (SUM(UNIX_TIMESTAMP(end_time) / (24 * 60 * 60) - UNIX_TIMESTAMP(start_time) / (24 * 60 * 60))) * 100
                           , 2) as progress
                        FROM common_project_equipment_schedule
                        WHERE project_id = %s
                        GROUP BY equipment_id
                       """, [project_id])
        progress_data = dict(cursor.fetchall())


    # 获取排期数据并按指定顺序排序
    schedules = Project_Equipment_Schedule.objects.filter(project_id=project_id).extra(
        select={
            'phase_order': "CASE phase WHEN 'SC' THEN 1 WHEN 'Y' THEN 2 WHEN 'T' THEN 3 WHEN 'X' THEN 4 WHEN 'A' THEN 5 WHEN 'D' THEN 5 END"},
        order_by=['equipment_id', 'phase_order']
    )

    # 获取设备信息
    equipment_info = Project_Equipment.objects.filter(project_id=project_id)
    equipment_dict = {eq.equipment_id: eq for eq in equipment_info}


    # 获取历史记录
    history = Project_Equipment_Schedule_History.objects.filter(project_id=project_id).order_by('-modified_at')

    return render(request, 'schedule_apply/schedule_apply_project.html', {
        'project': project,
        'schedules': schedules,
        'history': history,
        'progress_data': progress_data,
        'equipment_dict': equipment_dict
    })


    # # 执行原生SQL查询
    # with connection.cursor() as cursor:
    #     sql = """
    #           SELECT
    #                pes.project_id
    #               ,COALESCE(pbi.project_name,pes.project_id) as project_name -- 新增项目名称字段
    #               ,pes.equipment_id
    #               ,pes.equipment_name
    #               ,pes.equipment_quantity
    #               ,pes.phase
    #               ,pes.start_time
    #               ,pes.end_time
    #           FROM common_project_equipment_schedule pes
    #           LEFT JOIN common_project_equipment_schedule_history pbi
    #           ON pes.project_id = pbi.project_id
    #           ORDER BY pes.project_id, pes.equipment_id
    #           """
    #     cursor.execute(sql)
    #
    #     # 将查询结果转换为字典列表
    #     columns = [col[0] for col in cursor.description]
    #
    #     #情况1、用django ORM查询时，返回带时区对象，可自动转换时区
    #     #schedules = [dict(zip(columns, row)) for row in cursor.fetchall()]
    #
    #     #情况2、用原生SQL查询时，返回 原始字符串 或者 datetime对象但没有时区，需在Python层处理转换时区
    #     schedules = []
    #     for row in cursor.fetchall():
    #         row_dict = dict(zip(columns, row))
    #         # 转换时间字段
    #         for field in ['start_time', 'end_time']:
    #             # print("---------------- schedules 1111111 -------------")
    #             # print(type(row_dict[field]))
    #             # print(row_dict[field].tzinfo)
    #             if isinstance(row_dict[field], str):  # 处理字符串类型
    #                 naive_time = datetime.datetime.fromisoformat(row_dict[field])
    #                 aware_time = timezone.make_aware(naive_time, utc)
    #                 # print("---------------- schedules str aware_time -------------")
    #                 # print(aware_time)
    #                 # row_dict[field] = timezone.localtime(aware_time)
    #                 # print("---------------- schedules str row_dict[field] -------------")
    #                 print(row_dict[field])
    #             if isinstance(row_dict[field], datetime.datetime):  # 处理datetime类型
    #                 aware_time = timezone.make_aware(row_dict[field], utc)
    #                 # print("---------------- schedules datetime.datetime aware_time -------------")
    #                 # print(aware_time)
    #                 row_dict[field] = timezone.localtime(aware_time)
    #                 print("---------------- schedules datetime.datetime row_dict[field] -------------")
    #                 print(row_dict[field])
    #
    #         schedules.append(row_dict)
    #
    #
    # with connection.cursor() as cursor:
    #     history_sql = """
    #                   SELECT
    #                        sh.*
    #                       ,COALESCE(pbi.project_name, sh.project_id) AS project_name
    #                   FROM common_project_equipment_schedule_history sh
    #                   LEFT JOIN common_project_equipment_schedule_history pbi
    #                   ON sh.project_id = pbi.project_id
    #                   ORDER BY sh.modified_at DESC
    #                   """
    #     cursor.execute(history_sql)
    #     history_columns = [col[0] for col in cursor.description]
    #
    #     #情况1、用django ORM查询时，返回带时区对象，可自动转换时区
    #     # history = [dict(zip(history_columns, row)) for row in cursor.fetchall()]
    #
    #     #情况2、用原生SQL查询时，返回 原始字符串 或者 datetime对象但没有时区，需在Python层处理转换时区
    #     history = []
    #     for row in cursor.fetchall():
    #         row_dict = dict(zip(history_columns, row))
    #         # 转换时间字段
    #         for field in ['start_time', 'end_time', 'modified_at']:
    #             # print("---------------- history 1111111 -------------")
    #             # print(type(row_dict[field]))
    #             # print(row_dict[field].tzinfo)
    #             if isinstance(row_dict[field], str):  # 处理字符串类型
    #                 print("########################################## history ##########################################")
    #                 naive_time = datetime.datetime.fromisoformat(row_dict[field])
    #                 aware_time = timezone.make_aware(naive_time, utc)
    #                 # print("---------------- history str aware_time -------------")
    #                 # print(aware_time)
    #                 row_dict[field] = timezone.localtime(aware_time)
    #                 # print("---------------- history str row_dict[field] -------------")
    #                 # print(row_dict[field])
    #             if isinstance(row_dict[field], datetime.datetime):  # 处理字符串类型
    #                 aware_time = timezone.make_aware(row_dict[field], utc)
    #                 # print("---------------- history datetime.datetime aware_time -------------")
    #                 # print(aware_time)
    #                 row_dict[field] = timezone.localtime(aware_time)
    #                 # print("---------------- history datetime.datetime row_dict[field] -------------")
    #                 # print(row_dict[field])
    #
    #         history.append(row_dict)
    #
    # return render(request, 'schedule_apply/schedule_apply_project.html', {
    #      'schedules': schedules,
    #      'history': history
    # })
