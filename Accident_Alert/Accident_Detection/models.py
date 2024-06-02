from django.db import models

# Create your models here.

class Notifications(models.Model):
    n_id = models.AutoField(primary_key=True)
    notification = models.CharField(max_length = 1000)
    accident_date = models.DateTimeField(auto_now_add = True)
    latitude = models.FloatField(blank = True, null = True)
    longitude = models.FloatField(blank =True, null = True)
    accepted = models.IntegerField(blank = True, null = True)
    def __str__(self):
        return f"{self.n_id}"
    
class Hospital(models.Model):
    h_id = models.AutoField(primary_key = True, serialize = False)
    name = models.CharField(max_length = 256)
    email = models.EmailField(max_length = 256)
    h_lattitude = models.FloatField(blank = True, null = True)
    h_longitude = models.FloatField(blank = True, null = True)
    def __str__(self):
        return f"{self.h_id}-{self.name}"
