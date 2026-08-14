from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    failed_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def _str_(self):
        return self.user.username