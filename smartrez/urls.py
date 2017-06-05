from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'smartrez'
urlpatterns = [
url(r'^$', views.index, name = 'index'), #normal regex handling by django of urls to views, uses strings as args cause queries shouldn't be unique, a pizza query made again will redirect to the old pizza query with new images added if available
url(r'^(?P<query_term>[\w\-]+)/$', views.results, name='results'),
url(r'^(?P<query_term>[\w\-]+)/gallery/$', views.gallery, name='gallery'),
url(r'^(?P<query_term>[\w\-]+)/gallery_l/$', views.gallery_l, name='gallery_l'),
url(r'^q_create$', views.q_create, name='q_create'),
url(r'^(?P<query_term>[\w\-]+)/resize/$', views.resize, name='resize')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #handles serving of media files from smartresize/media/q_results, so in teh webpage, /smartrez/media/ is actually .../smartresize/media/q_results/

