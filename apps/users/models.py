from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('agent', 'Agent'),
        ('end_user', 'End User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)    
    def __str__(self):
        return f"{self.username} ({self.role})"