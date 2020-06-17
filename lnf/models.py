from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.BigIntegerField()

class Item(models.Model):
    name  = models.CharField(max_length=64)
    color = models.CharField(max_length=32)
    brand = models.CharField(max_length=32, blank=True)
    contents = models.CharField(max_length=128, blank=True)
    location = models.CharField(max_length=64)
    date = models.DateField(null=True)
    status = models.CharField(max_length=10)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploader', null=True)
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responder', blank=True, null=True)
    image = models.ImageField(upload_to='userImages', blank=True, null=True)

    def __str__(self):
        return f'Item: {self.name} Color: {self.color} Location: {self.location} Status: {self.status} Uploader: {self.uploader}'