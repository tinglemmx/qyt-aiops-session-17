from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from devices.models import DeviceMetric, MetricType,DeviceDB,MetricMapping
import pytz

def dashboard(request):
    return render(request, "dashboard/dashboard.html")

def get_metric_data(metric_logic_name_key_word, device_item, limit=20):
    cn_tz = pytz.timezone("Asia/Shanghai")

    metric_mappings = MetricMapping.objects.filter(
        logical_name__icontains=metric_logic_name_key_word,
        device_type_id=device_item.dev_type,
        is_primary=True
    )
    if not len(metric_mappings) ==1 :
        raise ValueError(f"找到多个或没有匹配的 MetricMapping for {metric_logic_name_key_word} on device {device_item.hostname}")
    series = []
    for mapping in metric_mappings:
        data_qs = DeviceMetric.objects.filter(
            device_id=device_item.id,
            metric_type_id=mapping.metric_type.id
        ).order_by('-timestamp')[:limit]
        data = list(reversed(data_qs))  # 倒序保证时间顺序

        series.append({
            "device": device_item.hostname,
            "metric": mapping.metric_type.name,
            "data": [
                {"timestamp": d.timestamp.astimezone(cn_tz).strftime("%Y-%m-%d %H:%M:%S"), "value": d.metrics.get("value", 0)}
                for d in data if d.success
            ]
        })
    return series
    
    
def dashboard_data(request):
    cpu_logic_kw = "cpuUsage"
    mem_logic_kw = "memoryPoolFree"

    # 假设你有一个 DeviceDB 模型
    devices = DeviceDB.objects.all()

    cpu_series = []
    mem_series = []

    for dev in devices:
        # 取最近 20 条 CPU 数据

        cpu_series.extend(get_metric_data(cpu_logic_kw, dev, limit=20))
        mem_series.extend(get_metric_data(mem_logic_kw, dev, limit=20))

    return JsonResponse({
        "cpu": cpu_series,
        "memory": mem_series,
    })