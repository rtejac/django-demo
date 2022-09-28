from django.db import models

# Create your models here.
class Destination(models.Model):

    # id feild will be given automatically by the DB
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='pics')
    price = models.IntegerField()
