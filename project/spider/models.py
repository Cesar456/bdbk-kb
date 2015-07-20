from django.db import models


# Create your models here.
class SpiderEntry(models.Model):
    url = models.CharField(max_length=512)
    actual_url = models.CharField(max_length=512, blank=True, null=True)
    redirect_chain = models.TextField(blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True, db_index=True)
    mongodb_id = models.CharField(max_length=128, blank=True, null=True)

    @staticmethod
    def getEntryForDownload(howmany):
        return list(SpiderEntry.objects.order_by('last_modified')[:howmany])
