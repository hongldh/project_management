from django.shortcuts import render
# Create your views here.
# schedule_apply_approve/views.py
from django.db import connection
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.utils import timezone
import datetime
from pytz import utc

@require_http_methods(["GET", "POST"])
# schedule_apply_approve/views.py
def approval_view(request):
    print("######################################################## count ########################################################")
    if request.method == 'POST':
        # project_id = request.POST['project_id']
        # equipment_id = request.POST['equipment_id']
        # phase = request.POST['phase']
        # modified_at_str = request.POST['modified_at']
        # 原始字符串格式如 "2023-10-01T12:34:56"
        # action = request.POST['action']
        selected_approvals = request.POST.getlist('selected_approvals')
        query_time = request.POST.get('query_time')
        print("~~~~~~~~~~~~~~~~~~~~~~~~~ query_time 2: ~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(query_time)
        print("############################ request.POST: ############################")
        print(request.POST)
        for item in selected_approvals:
            project_id, equipment_id, phase, modified_at_str = item.split('_')
            action = request.POST.get(f'action_{project_id}_{equipment_id}_{phase}_{modified_at_str}')
            # 转换为带时区的 datetime 对象
            local_tz = timezone.get_current_timezone()
            modified_at_naive = datetime.datetime.strptime(modified_at_str, "%Y-%m-%d %H:%M:%S")
            modified_at_aware = timezone.make_aware(modified_at_naive, local_tz)
            # 转换为 UTC 时间并截断到秒
            modified_at_utc = modified_at_aware.astimezone(utc)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~ modified_at_utc: ~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(modified_at_utc)
            with connection.cursor() as cursor:
                if action == 'approve':
                    cursor.execute("""
                        WITH TMP AS (
                            SELECT project_id, equipment_id, phase, start_time, end_time
                            FROM common_project_equipment_schedule_history
                            WHERE project_id = %s AND equipment_id = %s AND phase = %s AND SUBSTRING(modified_at, 1, 19) = SUBSTRING(%s, 1, 19) AND processed_flag = 0
                        )
                        UPDATE common_project_equipment_schedule AS CPES
                        INNER JOIN TMP ON CPES.project_id = TMP.project_id AND CPES.equipment_id = TMP.equipment_id AND CPES.phase = TMP.phase
                        SET CPES.start_time = TMP.start_time
                           ,CPES.end_time = TMP.end_time
                        ;
                    """, [project_id, equipment_id, phase, modified_at_utc])
                    cursor.execute("""
                        UPDATE common_project_equipment_schedule_history
                        SET processed_flag = 1
                        WHERE project_id = %s AND equipment_id = %s AND phase = %s AND SUBSTRING(modified_at,1,19)=SUBSTRING(%s,1,19)
                        ;
                    """, [project_id, equipment_id, phase,modified_at_utc])
                else:
                    cursor.execute("""
                        UPDATE common_project_equipment_schedule_history
                        SET processed_flag = -1
                        WHERE project_id = %s AND equipment_id = %s AND phase = %s AND SUBSTRING(modified_at,1,19)=SUBSTRING(%s,1,19)
                    """, [project_id, equipment_id, phase,modified_at_utc])
                cursor.execute("""
                    UPDATE common_project_equipment_schedule_history
                    SET processed_flag = -2
                    WHERE project_id = %s AND equipment_id = %s AND phase = %s AND SUBSTRING(modified_at,1,19) <= SUBSTRING(%s,1,19) AND processed_flag = 0
                """, [project_id, equipment_id, phase,query_time])
        return redirect('.')
    #GET请求
    with connection.cursor() as cursor:
        # 获取所有排期信息
        cursor.execute("""
            SELECT s.project_id, s.equipment_id, s.phase, e.equipment_quantity, s.start_time, s.end_time
            FROM common_project_equipment_schedule s
            LEFT JOIN common_project_equipment e
             ON s.project_id = e.project_id AND s.equipment_id = e.equipment_id
            LEFT JOIN common_project_basic b
             ON s.project_id = b.project_id
            WHERE b.project_id IS NOT NULL
             AND e.project_id IS NOT NULL AND e.equipment_id IS NOT NULL
            ORDER BY s.project_id, s.equipment_id, s.phase

        """)
        raw_schedules = cursor.fetchall()
        schedules = []
        for item in raw_schedules:
            # 转换第4、5列（start_time, end_time）
            converted = list(item)
            for i in [4, 5]:  # 根据查询字段顺序调整索引
                if isinstance(converted[i], datetime.datetime):
                    # 将 naive datetime 转换为 UTC 时区
                    converted[i] = timezone.make_aware(converted[i], utc)
            schedules.append(tuple(converted))
        query_time = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~ query_time 1: ~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(query_time)
        # 获取待审批记录
        cursor.execute("""
            SELECT tmp.project_id, tmp.equipment_id, tmp.phase, e.equipment_quantity, tmp.start_time, tmp.end_time, tmp.modified_at
            FROM (
                SELECT project_id, equipment_id, phase, start_time, end_time, modified_at,
                       ROW_NUMBER() OVER (
                           PARTITION BY project_id, equipment_id, phase
                           ORDER BY modified_at DESC
                       ) as rn
                FROM common_project_equipment_schedule_history
                WHERE processed_flag = 0
            ) tmp
            LEFT JOIN common_project_equipment e
             ON tmp.project_id = e.project_id AND tmp.equipment_id = e.equipment_id
            LEFT JOIN common_project_basic b
             ON tmp.project_id = b.project_id
            WHERE tmp.rn = 1
            AND b.project_id IS NOT NULL
            AND e.project_id IS NOT NULL AND e.equipment_id IS NOT NULL
        """)
        # 添加时区转换
        raw_pending = cursor.fetchall()
        # print("raw_pending[0][6]:")
        # print(raw_pending[0][6])
        # print(raw_pending[0][6].tzinfo)
        pending_approvals = []
        for item in raw_pending:
            # 转换第4、5、6列（start_time, end_time, modified_at）
            converted = list(item)
            for i in [4, 5, 6]:  # 根据查询字段顺序调整索引
                if isinstance(converted[i], datetime.datetime):
                    # 将 naive datetime 转换为 UTC 时区
                    converted[i] = timezone.make_aware(converted[i], utc)
            pending_approvals.append(tuple(converted))
        # print("pending_approvals[0][6]:")
        # print(pending_approvals[0][6])
        # print(pending_approvals[0][6].tzinfo)
        return render(request, 'schedule_apply_approve/approval.html', {
            'schedules': schedules,
            'pending_approvals': pending_approvals,
            'query_time': query_time
        })
