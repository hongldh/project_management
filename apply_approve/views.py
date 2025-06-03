from django.shortcuts import render

# Create your views here.
# apply_approve/views.py
from django.db import connection
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.utils import timezone
import datetime
from pytz import utc


@require_http_methods(["GET", "POST"])
# apply_approve/views.py
def approval_view(request):
    print("######################################################## count ########################################################")
    if request.method == 'POST':
        # project_id = request.POST['project_id']
        # equipment_id = request.POST['equipment_id']
        # phase = request.POST['phase']
        # modified_at_str = request.POST['modified_at']  # 原始字符串格式如 "2023-10-01T12:34:56"
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
                        UPDATE common_projectequipmentschedule
                        SET 
                            equipment_quantity = (
                                SELECT equipment_quantity 
                                FROM common_schedulehistory 
                                WHERE project_id = %s 
                                  AND equipment_id = %s 
                                  AND phase = %s 
                                  AND SUBSTRING(modified_at,1,19)=SUBSTRING(%s,1,19)
                                  AND processed_flag = 0
                            ),
                            start_time = (
                                SELECT start_time 
                                FROM common_schedulehistory 
                                WHERE project_id = %s 
                                  AND equipment_id = %s 
                                  AND phase = %s
                                  AND SUBSTRING(modified_at,1,19)=SUBSTRING(%s,1,19)
                                  AND processed_flag = 0
                            ),
                            end_time = (
                                SELECT end_time 
                                FROM common_schedulehistory 
                                WHERE project_id = %s 
                                  AND equipment_id = %s 
                                  AND phase = %s
                                  AND SUBSTRING(modified_at,1,19)=SUBSTRING(%s,1,19)
                                  AND processed_flag = 0
                            )
                        WHERE 
                            project_id = %s 
                            AND equipment_id = %s 
                            AND phase = %s
                        ;
                    """, [project_id, equipment_id, phase,modified_at_utc,project_id, equipment_id, phase,modified_at_utc,project_id, equipment_id, phase,modified_at_utc,project_id, equipment_id, phase])

                    cursor.execute("""
                        UPDATE common_schedulehistory
                        SET processed_flag = 1
                        WHERE project_id = %s 
                        AND equipment_id = %s
                        AND phase = %s
                        AND SUBSTRING(modified_at,1,19)=SUBSTRING(%s,1,19)
                        ;
                    """, [project_id, equipment_id, phase,modified_at_utc])
                else:
                    cursor.execute("""
                        UPDATE common_schedulehistory
                        SET processed_flag = -1
                        WHERE project_id = %s 
                        AND equipment_id = %s
                        AND phase = %s
                        AND SUBSTRING(modified_at,1,19)=SUBSTRING(%s,1,19)
                    """, [project_id, equipment_id, phase,modified_at_utc])

                cursor.execute("""
                    UPDATE common_schedulehistory
                    SET processed_flag = -2
                    WHERE project_id = %s 
                    AND equipment_id = %s
                    AND phase = %s
                    AND SUBSTRING(modified_at,1,19) <= SUBSTRING(%s,1,19)
                    AND processed_flag = 0
                """, [project_id, equipment_id, phase,query_time])

        return redirect('.')


    with connection.cursor() as cursor:
        # 获取所有排程信息
        cursor.execute("""
            SELECT project_id, equipment_id, phase, equipment_quantity, start_time, end_time 
            FROM common_projectequipmentschedule
            ORDER BY project_id, equipment_id, phase
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
            SELECT sh.project_id, sh.equipment_id, sh.phase, 
                   sh.equipment_quantity, sh.start_time, sh.end_time, sh.modified_at
            FROM (
                SELECT project_id, equipment_id, phase, MAX(modified_at) as max_time 
                FROM common_schedulehistory 
                WHERE processed_flag = 0 
                GROUP BY project_id, equipment_id, phase
            ) latest 
            JOIN common_schedulehistory sh 
            ON sh.project_id = latest.project_id 
            AND sh.equipment_id = latest.equipment_id 
            AND sh.phase = latest.phase 
            AND sh.modified_at = latest.max_time
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

    return render(request, 'apply_approve/approval.html', {
        'schedules': schedules,
        'pending_approvals': pending_approvals,
        'query_time': query_time
    })

