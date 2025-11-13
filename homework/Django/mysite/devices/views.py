from django.shortcuts import render, get_object_or_404
from .models import DeviceDB, DeviceMetric
from scripts.snmp_collector import collect_snmp_for_device

def collect_once(request):
    devices = DeviceDB.objects.all()
    metrics = []

    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        device = get_object_or_404(DeviceDB, id=device_id)
        collect_snmp_for_device(device)
        metrics = DeviceMetric.objects.filter(device=device).order_by('-timestamp')

    return render(request, 'devices/collect.html', {'devices': devices, 'metrics': metrics})
