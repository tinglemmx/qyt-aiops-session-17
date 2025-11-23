from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta,datetime
from devices.models import DeviceMetric, MetricType,DeviceDB,MetricMapping
import pytz
from .services.metric_service import MetricService
import random
from django.contrib.auth.decorators import login_required

def dashboard(request):
    return render(request, "dashboard/dashboard.html")

def dashboard_data(request):
    ms = MetricService(max_points=20)

    cpu_logic_kw = "cpuUsage"
    mem_logic_kw = "memoryPoolFree"
    mem_logic_used_kw = "memoryPoolUsed"
    
    devices = DeviceDB.objects.all()

    cpu_all = []
    mem_all = []
    mem_avail = []
    mem_used = []

    for dev in devices:
        cpu_all.append(ms.get_device_series(dev, cpu_logic_kw))
        mem_all.append(ms.get_device_series(dev, mem_logic_kw))
        mem_avail.append(ms.get_device_series(dev, mem_logic_kw))
        mem_used.append(ms.get_device_series_memory_used(dev))


    # print(mem_used)
    cpu_x, cpu_series = ms.merge_series(cpu_all)
    mem_x, mem_series = ms.merge_series(mem_all)
    mem_avail_x, mem_avail_series = ms.merge_series(mem_avail)
    mem_used_x, mem_used_serise = ms.merge_series(mem_used)

    return JsonResponse(ms.build_echarts_json(
        cpu_data={"x": cpu_x, "series": cpu_series},
        mem_data={"x": mem_x, "series": mem_series},
        mem_avail_data={"x": mem_avail_x, "series": mem_avail_series},
        mem_used_data={"x": mem_used_x, "series": mem_used_serise},
    ))
@login_required()
def ultimate_line(request):
    return render(request, "dashboard/ultimate_line.html")

@login_required()
def cpu_data_api(request):
    ms = MetricService(max_points=100)
    cpu_logic_kw = "cpuUsage"
    devices = DeviceDB.objects.all()
    cpu_all = []
    for dev in devices:
        cpu_all.append(ms.get_device_series(dev, cpu_logic_kw))
    cpu_x, cpu_series = ms.merge_series(cpu_all)
    cpu_data={"times": cpu_x, "series": cpu_series}
    return JsonResponse(cpu_data)

def area_simple(request):
    return render(request, "dashboard/area-simple.html")

@login_required()
def qyt_device_echarts_final_line_if_speed_class(request):
    return render(request, "dashboard/qyt_device_echarts_final_line_if_speed.html")

def final_line_if_speed_data_api(request):
    now = datetime.now()
    num_points = 20
    legends = ["eth0-up", "eth0-down", "eth1-up", "eth1-down"]  # 模拟几个接口
    datas = []

    for name in legends:
        series_data = []
        for i in range(num_points):
            t = now - timedelta(seconds=(num_points - 1 - i) * 30)  # 每 30 秒一个点
            value = random.randint(0, 1000 * 1024)  # 模拟速率，单位 bps
            series_data.append([t.strftime("%Y-%m-%d %H:%M:%S"), value])
        datas.append({
            "name": name,
            "type": "line",
            "smooth": True,
            "showSymbol": False,
            "data": series_data
        })


    starttime = (now - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "labelname": "接口流量",
        "lengends": legends,
        "datas": datas,
        "starttime": starttime
    }
    return JsonResponse(data)