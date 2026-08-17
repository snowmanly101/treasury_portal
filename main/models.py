from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  account_number = models.CharField(max_length=50)
  routing_id = models.CharField(max_length=50)
  balance = models.CharField(max_length=50)
  account_type = models.CharField(max_length=50)
  is_locked = models.BooleanField(default=True)

  def _str_(self):
    return f'{self.user.username} Profile'


class Transaction(models.Model):
  # Changed from User to UserProfile so the admin inline works perfectly
  user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  date = models.CharField(max_length=50)
  ref = models.CharField(max_length=50)
  company = models.CharField(max_length=255)
  amount = models.CharField(max_length=50)
  status = models.CharField(max_length=50)

  def _str_(self):
    return f'{self.ref} - {self.amount}'