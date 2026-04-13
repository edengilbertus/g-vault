from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from finance.models import SavingsAccount


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_member_savings_account(sender, instance, created, **kwargs):
    if created:
        SavingsAccount.objects.get_or_create(member=instance)
