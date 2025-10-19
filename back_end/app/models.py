from django.db import models

# Create your models here.
class Personality(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')

    REQUIRED_FIELDS = ['name', 'description', 'image']
    
    def __str__(self):
        return self.name