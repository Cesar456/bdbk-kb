from django.db import models

class Relation(models.Model):
     subject = models.CharField(max_length=255)
     verb = models.CharField(max_length=255)
     target = models.TextField()
