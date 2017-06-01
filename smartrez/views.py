from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import SearchQuery, Img, Selected_imgs
from django.views import generic
from django.urls import reverse
from django.template import loader
from .titles import ImageScraper
import subprocess
import threading
import itertools
import time
from django.conf import settings
import os
from os.path import basename
import zipfile
def q_create(request):
  name = request.POST['term'].replace(' ','_')+'_'+str(round(time.time()))
  q = SearchQuery(term = name)
  q.save()
  IS = ImageScraper()
  thumb_list, img_list = IS.get_img(srch = request.POST['term'])
  for thumb, img in itertools.zip_longest(thumb_list, img_list):
   q.img_set.create(img_url = img, thumb_url = thumb)
  return HttpResponseRedirect(reverse('smartrez:results', args = (name,)))
def index(request):
 template = loader.get_template('smartrez/index.html')
 context = {}
 return HttpResponse(template.render(context, request))
def results(request, query_term):
 query = get_object_or_404(SearchQuery,term=query_term)
 template = loader.get_template('smartrez/results.html')
 context = {'query': query,'query_name' : query.term.replace('_',' ')}
 return HttpResponse(template.render(context, request))
def smartcrop(width, height, query_term, file):
    subprocess.run(['smartcrop --width %s --height %s "%s" "%s"' % (width, height, (settings.MEDIA_ROOT + query_term + '/' + file), (settings.MEDIA_ROOT + query_term + '/' + file))],shell=True)
def resize(request, query_term):
 query = get_object_or_404(SearchQuery,term=query_term)
 path = settings.MEDIA_ROOT + query_term
 ziph = zipfile.ZipFile(settings.MEDIA_ROOT + query_term + '.zip', 'w', zipfile.ZIP_DEFLATED)
 urlstring = request.POST['act_img']
 urllist = urlstring.split(',')
 urllist = urllist [:-1]
 real_imglist = []
 for url in urllist:
  q_obj = query.img_set.get(thumb_url=url)
  real_imglist.append(q_obj.img_url)
 width = request.POST['width']
 height = request.POST['height']
 IS = ImageScraper()
 filelist = IS.save_imgs(urllist=real_imglist, query_name = query.term)
 threaddict = {}
 counter = 0
 for file in filelist:
  threaddict[counter] = threading.Thread(target=smartcrop, args=(width, height,query.term,file))
  threaddict[counter].daemon = True
  threaddict[counter].start()
  counter += 1
 threaddict[counter-1].join()
 for file in filelist:
         ziph.write(settings.MEDIA_ROOT + query_term +'/' +file, basename(settings.MEDIA_ROOT + query_term +'/' +file))
 ziph.close()
 template = loader.get_template('smartrez/resized.html')
 context = {'query' : query, 'filelist' : filelist, 'zipname' : query_term + '.zip'}
 return HttpResponse(template.render(context, request))
 

