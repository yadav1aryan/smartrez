from django.db import models
class SearchQuery(models.Model):
 term = models.CharField(max_length = 200)
class Img(models.Model):
 search_query = models.ForeignKey(SearchQuery, on_delete = models.CASCADE)
 img_url = models.CharField(max_length = 200)
 thumb_url = models.CharField(max_length = 200)
 uses = models.IntegerField(default=0)
 img_id = models.IntegerField(default=0)

# Create your models here.
