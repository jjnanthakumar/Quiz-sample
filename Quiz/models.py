from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category_id = models.CharField(max_length=3)
    category_diff = models.IntegerField(default=0)
    category_name = models.CharField(default='choose', max_length=20)
    time_taken = models.CharField(default='0.0', max_length=500)
    score = models.IntegerField(default=0)


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category = models.ManyToManyField(Category, null=True)
