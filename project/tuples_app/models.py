from django.db import models

class Relation(models.Model):
     subject = models.CharField(max_length=255, db_index=True)
     verb = models.CharField(max_length=255, db_index=True)
     target = models.TextField()
