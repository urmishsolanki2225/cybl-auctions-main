from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Assign all permissions to the Super Admin group'

    def handle(self, *args, **kwargs):
        super_admin_group, _ = Group.objects.get_or_create(name='Super Admin')
        all_permissions = Permission.objects.all()
        super_admin_group.permissions.set(all_permissions)

        self.stdout.write(self.style.SUCCESS('Successfully assigned all permissions to Super Admin group'))
