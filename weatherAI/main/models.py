from django.db import models
from django.contrib.auth.models import User  

# Create your models here.
class reading(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    max_temp=models.FloatField()
    min_temp=models.FloatField()
    real_temp=models.FloatField()
    max_feel=models.FloatField()
    min_feel=models.FloatField()
    humidity=models.IntegerField()
    pressure=models.FloatField()
    date=models.DateTimeField(auto_now_add=True)
    prediction=models.CharField(max_length=30,null=True,blank=True)