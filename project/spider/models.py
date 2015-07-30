from django.db import models


# data migration must be performed on every schema update
# version: 2

# Create your models here.
class SpiderEntry(models.Model):
    '''
    Ver: 2

    Database Schema:
    url: url of this entry.
    actual_url: real url after HTTP redirects. null=<new entry>
    redirect_chain: how was url ==> actual_url, urls are split by newline(\n). (currently not used)
    last_modified: last this entry was modifed(downloaded). null=<new entry>
    mongodb_id: where is this page stored in mongodb. null=<not existing>
    '''
    url = models.CharField(max_length=255, unique=True)
    actual_url = models.CharField(max_length=512, blank=True, null=True)
    redirect_chain = models.TextField(blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True, db_index=True)
    mongodb_id = models.CharField(max_length=128, blank=True, null=True)

    @staticmethod
    def getEntryForDownload(howmany):
        return list(SpiderEntry.objects.order_by('last_modified')[:howmany])
