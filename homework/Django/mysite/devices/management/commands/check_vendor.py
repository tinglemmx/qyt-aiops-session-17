from django.core.management.base import BaseCommand
from devices.models import DeviceType

class Command(BaseCommand):
    help = "just test command to check vendor field"

    def handle(self, *args, **options):
        for dt in DeviceType.objects.all():
            self.stdout.write(f"{dt.name} <--> {dt.vendor_fk}")  # vendor_fk 是外键对象
