from django.shortcuts import render, get_object_or_404,redirect
from .models import DeviceDB, DeviceMetric
from scripts.snmp_collector import collect_snmp_for_device
from .forms import DeviceForm
from django.db.models import Q
from django.contrib import messages


def collect_once(request):
    devices = DeviceDB.objects.all()
    metrics = []

    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        device = get_object_or_404(DeviceDB, id=device_id)
        collect_snmp_for_device(device)
        metrics = DeviceMetric.objects.filter(device=device).order_by('-timestamp')

    return render(request, 'devices/collect.html', {'devices': devices, 'metrics': metrics})

def add_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            ip = form.cleaned_data["ip_address"]
            duplicate = DeviceDB.objects.filter(ip_address=ip).exists()
            if duplicate and request.POST.get("confirm_duplicate") != "1":
                # IP 重复，先显示模板，触发 JS 弹窗
                return render(request, "devices/add_device.html", {
                    "form": form,
                    "duplicate_ip": ip,
                    "show_duplicate_confirm": True  # 新增标记

                })
            form.save()
            return redirect("device_list")  # 保存后跳回列表页
    else:
        form = DeviceForm()
    return render(request, "devices/device_form.html",{"form": form, "mode":"add"})

def device_list(request):
    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "id")       # 默认按 id
    direction = request.GET.get("dir", "asc")  # 默认升序

    # 组合排序字段
    sort_field = f"-{sort}" if direction == "desc" else sort

    devices = DeviceDB.objects.all()

    # 搜索
    if q:
        devices = devices.filter(
            Q(hostname__icontains=q) |
            Q(ip_address__icontains=q)
        )

    # 排序
    devices = devices.order_by(sort_field)

    return render(request, "devices/list.html", {
        "devices": devices,
        "q": q,
        "current_sort": sort,
        "current_dir": direction,
    })


def edit_device(request, device_id):
    device = get_object_or_404(DeviceDB, pk=device_id)

    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect("device_list")
    else:
        form = DeviceForm(instance=device)

    return render(request, "devices/device_form.html", {"form": form, "device": device,"mode":"edit"})

def delete_device(request, pk):
    device = get_object_or_404(DeviceDB, pk=pk)
    device.delete()
    messages.success(request, f"设备 {device.hostname} 删除成功！")
    return redirect("device_list")