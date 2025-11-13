from django.core.management.base import BaseCommand
from devices.models import DeviceType, Vendor



class Command(BaseCommand):
    help = "Migrate DeviceType.vendor string field into Vendor table"

    def handle(self, *args, **options):
        for dt in DeviceType.objects.all():
            if dt.vendor:
                vendor_obj = Vendor.objects.filter(name=dt.vendor).first()
                if vendor_obj:
                    self.stdout.write(f"{dt.id}: Vendor already set -> {dt.vendor}")
                    continue

            vendor_obj, created = Vendor.objects.get_or_create(name=dt.vendor)
            dt.vendor_rt = vendor_obj
            dt.save()
            self.stdout.write(f"{dt.id}: Vendor set -> {vendor_obj.name} (created={created})")
