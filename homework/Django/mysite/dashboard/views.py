from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from devices.models import DeviceMetric, MetricType,DeviceDB,MetricMapping
import pytz
from .services.metric_service import MetricService

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

def ultimate_line(request):
    return render(request, "dashboard/ultimate_line.html")