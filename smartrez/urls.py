from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'smartrez'
urlpatterns = [
url(r'^$', views.index, name = 'index'),
url(r'^(?P<query_term>[\w\-]+)/$', views.results, name='results'),
url(r'^q_create$', views.q_create, name='q_create'),
url(r'^(?P<query_term>[\w\-]+)/resize/$', views.resize, name='resize')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

