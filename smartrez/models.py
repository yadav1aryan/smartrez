from django.db import models
class SearchQuery(models.Model): #a searchquery view to hold the name of a query
 term = models.CharField(max_length = 200)
class Img(models.Model): #holds images for each search query, utilises foreign key to maintain images for each query
 search_query = models.ForeignKey(SearchQuery, on_delete = models.CASCADE) #self explanatory field names
 img_url = models.CharField(max_length = 200)
 thumb_url = models.CharField(max_length = 200)
 uses = models.IntegerField(default=0)
 img_id = models.IntegerField(default=0)
