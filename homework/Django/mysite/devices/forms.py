from django import forms
from .models import DeviceDB

class DeviceForm(forms.ModelForm):
    class Meta:
        model = DeviceDB
        fields = [
            "hostname",
            "ip_address",
            "description",
            "dev_type",
            "snmp_ro_community",
            "snmp_rw_community",
            "ssh_username",
            "ssh_password",
            "enable_password",
        ]
