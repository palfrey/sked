from django.db import models

class GoogleUser(models.Model):
    email = models.EmailField(primary_key=True)
    token = models.CharField(max_length=255)
    name = models.CharField(max_length=255)