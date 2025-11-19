from django.db import models
from django.utils import timezone


class Vendor(models.Model):
    """厂商，例如 Cisco, Juniper, Arista"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    """设备类型，例如 Cisco Router, Juniper Switch 等"""
    name = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(
        'Vendor', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('vendor', 'name')

    def __str__(self):
        return f"{self.vendor} {self.name}"


class DeviceDB(models.Model):
    """设备基本信息"""
    hostname = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    description = models.TextField(blank=True, null=True)
    dev_type = models.ForeignKey(
        DeviceType, on_delete=models.SET_NULL, null=True)
    snmp_ro_community = models.CharField(max_length=100, default='public')
    snmp_rw_community = models.CharField(max_length=100, default='private')
    ssh_username = models.CharField(max_length=100, blank=True, null=True)
    ssh_password = models.CharField(max_length=100, blank=True, null=True)
    enable_password = models.CharField(max_length=100, blank=True, null=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"


class MetricType(models.Model):
    """定义指标类型，可映射到不同的采集协议与路径"""
    PROTOCOL_CHOICES = [
        ("snmp", "SNMP"),
        ("grpc", "gRPC"),
        ("telemetry", "Telemetry"),
        ("restconf", "RESTCONF"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100)
    protocol = models.CharField(
        max_length=50, choices=PROTOCOL_CHOICES, default="snmp")
    metric_path = models.CharField(max_length=300)  # OID 或 gRPC Path
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ("name", "protocol", "metric_path")
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["protocol"]),
        ]

    def __str__(self):
        return f"{self.name} [{self.protocol}:{self.metric_path}]"


class MetricMapping(models.Model):
    """定义逻辑指标与实际采集指标 (MetricType) 的关系"""
    logical_name = models.CharField(max_length=100)
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)

    class Meta:
        unique_together = ("logical_name", "metric_type","device_type")
        indexes = [
            models.Index(fields=["logical_name"]),
        ]

    def __str__(self):
        return f"{self.logical_name}:{self.device_type} → {self.metric_type.protocol}:{self.metric_type.metric_path}"


class DeviceMetric(models.Model):
    """设备采集的实际指标数据"""
    device = models.ForeignKey(DeviceDB, on_delete=models.CASCADE)
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)  # 存 UTC 时间
    # {"value": 23.5} 或 {"value": {"rx": 1024, "tx": 2048}}
    metrics = models.JSONField()
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["device", "timestamp"]),
            models.Index(fields=["metric_type"]),
        ]

    def __str__(self):
        return f"{self.device.hostname} @ {self.timestamp.isoformat()} ({self.metric_type.name})"
