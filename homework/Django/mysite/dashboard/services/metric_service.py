from django.utils import timezone
from devices.models import DeviceMetric, MetricMapping, DeviceDB
import pytz

class MetricService:
    def __init__(self, max_points=20):
        self.max_points = max_points
        self.tz = pytz.timezone("Asia/Shanghai")

    # ---------------------
    # 通用方法：根据逻辑名获取设备的指标序列
    # ---------------------
    def get_device_series(self, device, logic_keyword):
        mappings = MetricMapping.objects.filter(
            logical_name__icontains=logic_keyword,
            device_type_id=device.dev_type,
            is_primary=True
        )

        if len(mappings) > 1:
            raise ValueError(f"{device.hostname} 找到多个匹配的 MetricMapping for {logic_keyword}")
        elif len(mappings) == 1:
            mapping = mappings[0]
        else:
            return None
            
        mapping = mappings.first()

        metrics = DeviceMetric.objects.filter(
            device_id=device.id,
            metric_type_id=mapping.metric_type.id,
        ).order_by('-timestamp')[:self.max_points]

        metrics = list(reversed(metrics))

        times = []
        values = []

        for m in metrics:
            # if not m.success:
            #     continue
            times.append(m.timestamp.astimezone(self.tz).strftime("%Y-%m-%d %H:%M:%S"))
            if m.success:
                values.append(float(m.metrics.get("value", 0)))
            else:
                values.append(None)

        return {
            "device": device.hostname,
            "metric": mapping.metric_type.name,
            "times": times,
            "values": values,
            "mapping": mapping,  # preserve mapping for unit type
        }

    def get_device_series_memory_used(self, device):
        vendor_name = device.dev_type.vendor.name if device.dev_type and device.dev_type.vendor else None
        # print("Vendor Name:", vendor_name)
        if vendor_name == "Cisco":
            logic_keyword = "memoryPoolUsed"
            memory_used = self.get_device_series(device, logic_keyword)
            memory_used_list = [ int(item) if item is not None else None for item in memory_used["values"]]
            memory_used["values"] = memory_used_list
            return memory_used
        elif vendor_name == "VyOS":
            memory_total = self.get_device_series(device, "memoryPoolTotal")
            memory_total_list = memory_total['values']
            memory_available_list = self.get_device_series(device, "memoryPoolFree")['values']
            # print(memory_total_list)
            # print("----------------------")
            # print(memory_available_list)
            memory_used_list = [
                int(t - a) if (t is not None and a is not None) else None
                for t, a in zip(memory_total_list, memory_available_list)
            ]
            return {
            "device": device.hostname,
            "metric": "memory_used(calculated)",
            "times": memory_total["times"],
            "values": memory_used_list,
            "mapping": memory_total["mapping"],  # preserve mapping for unit type
        }

        elif vendor_name == "Juniper":
            logic_keyword = "memoryPoolUsed"
        else:
            print(f"Unknown vendor for device {device.hostname}, skipping memory used retrieval.")
            return None
        
 
        
    # ---------------------
    # 将多个设备的同类型指标合并
    # ---------------------
    def merge_series(self, series_list):
        # 默认：以第一个时间序列为基准
        x_axis = []
        series_arr = []

        if series_list:
            x_axis = series_list[0]["times"]

        for s in series_list:
            series_arr.append({
                "name": f"{s['device']} ({s['metric']})",
                "type": "line",
                "smooth": True,
                "showSymbol": False,
                "data": self.apply_unit_conversion(s),
            })

        return x_axis, series_arr

    # ---------------------
    # 自动进行单位转换（KB → B、Byte 输出格式等）
    # ---------------------
    def apply_unit_conversion(self, series_info):
        mapping = series_info["mapping"]

        # 如果 MetricMapping 里扩展一个字段，如 "unit": "KB"
        if hasattr(mapping.metric_type, "unit") and mapping.metric_type.unit == "KB":
            # print("apply_unit_conversion: " + mapping.metric_type.unit)
            return [int(v / 1024) if v is not None else None for v in series_info["values"]]
        
        if hasattr(mapping.metric_type, "unit") and mapping.metric_type.unit == "B":
            # print("apply_unit_conversion: " + mapping.metric_type.unit)
            return [int(v / 1024 / 1024) if v is not None else None for v in series_info["values"]]


        # 自动判断 (heuristic)
        values = series_info["values"]
        # print("Auto unit conversion check for values:", values)
        # numeric_values = [v for v in values if v is not None]
        # if numeric_values and max(numeric_values) < 10_000_000:
        #     values = [v*1024 if v is not None else None for v in values]

        return values

    # ---------------------
    # 统一生成 ECharts JSON 格式
    # ---------------------
    def build_echarts_json(self, cpu_data, mem_data,mem_avail_data,mem_used_data):
        return {
            "cpu": {
                "x": cpu_data["x"],
                "series": cpu_data["series"]
            },
            "memory": {
                "x": mem_data["x"],
                "series": mem_data["series"]
            },
            "memory_avail": {
                "x": mem_avail_data["x"],
                "series": mem_avail_data["series"]
            },
            "memory_used": {
                "x": mem_used_data["x"],
                "series": mem_used_data["series"]
            }
        }
