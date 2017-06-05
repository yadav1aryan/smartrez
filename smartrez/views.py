from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import SearchQuery, Img
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
from os import listdir
from os.path import isfile, join
from os.path import basename
import zipfile
def q_create(request):
  name = request.POST['term'].replace(' ','_').lower()
  try:
   IS = ImageScraper()
   q = SearchQuery.objects.get(term=name)
   thumb_list, img_list, pixabay_id = IS.get_img(srch = request.POST['term'], type= request.POST['type'])
   for img,thumb, id in itertools.zip_longest(img_list, thumb_list, pixabay_id):
    try:
     k = q.img_set.get(img_id = id)
    except:
     q.img_set.create(img_url = img, thumb_url = thumb, img_id = id)
  except:
   q = SearchQuery(term = name)
   q.save()
   IS = ImageScraper()
   thumb_list, img_list, pixabay_id = IS.get_img(srch = request.POST['term'], type= request.POST['type'])
   for thumb, img, id in itertools.zip_longest(thumb_list, img_list, pixabay_id):
    q.img_set.create(img_url = img, thumb_url = thumb, img_id = id)
  return HttpResponseRedirect(reverse('smartrez:results', args = (name,)))
def index(request):
 querylist = []
 for query in SearchQuery.objects.all():
  querylist.append(query.term)
 template = loader.get_template('smartrez/index.html')
 context = {'querylist' : querylist}
 return HttpResponse(template.render(context, request))
def results(request, query_term):
 query = get_object_or_404(SearchQuery,term=query_term)
 template = loader.get_template('smartrez/results.html')
 context = {'query': query,'query_name' : query.term.replace('_',' ')}
 return HttpResponse(template.render(context, request))
def smartcrop(width, height, query_term, file):
    subprocess.run(['smartcrop --width %s --height %s "%s" "%s"' % (width, height, (settings.MEDIA_ROOT + query_term + '/edited/' + file), (settings.MEDIA_ROOT + query_term + '/edited/' + file))],shell=True)
    subprocess.run(['magick %s -compress JPEG -quality 80 %s' % ((settings.MEDIA_ROOT + query_term + '/edited/' + file), (settings.MEDIA_ROOT + query_term + '/edited/' + file))],shell=True)
def resize(request, query_term):
 query = get_object_or_404(SearchQuery,term=query_term)
 path = settings.MEDIA_ROOT + query_term
 ziph = zipfile.ZipFile(settings.MEDIA_ROOT + query_term + '.zip', 'w', zipfile.ZIP_DEFLATED)
 filestring = request.POST['act_img']
 filelist = filestring.split(',')
 editlist = filelist [:-1]
 filelist = [f for f in listdir(settings.MEDIA_ROOT + query_term +'/edited') if isfile(join(settings.MEDIA_ROOT + query_term +'/edited', f))]
 real_imglist = []
 width = request.POST['width']
 height = request.POST['height']
 threaddict = {}
 for counter, file in enumerate(editlist):
  threaddict[counter] = threading.Thread(target=smartcrop, args=(width, height,query.term,file))
  threaddict[counter].daemon = True
  threaddict[counter].start()
 for key in threaddict.keys():
  threaddict[key].join()

 # for file in filelist:
 #         ziph.write(settings.MEDIA_ROOT + query_term +'/' +file, basename(settings.MEDIA_ROOT + query_term +'/' +file))
 # ziph.close()
 print(filelist)
 template = loader.get_template('smartrez/gallery.html')
 context = {'query' : query, 'filelist' : filelist}
 return HttpResponse(template.render(context, request))
def gallery(request, query_term):
    query = get_object_or_404(SearchQuery, term=query_term)
    urlstring = request.POST['act_img']
    urllist = urlstring.split(',')
    urllist = urllist[:-1]
    real_imglist = []
    for url in urllist:
        q_obj = query.img_set.get(thumb_url=url)
        q_obj.uses += 1
        q_obj.save()
        real_imglist.append(q_obj.img_url)
    IS = ImageScraper()
    filelist = IS.save_imgs(urllist=real_imglist, query_name=query.term)
    template = loader.get_template('smartrez/gallery.html')
    context = {'query': query, 'filelist': filelist}
    return HttpResponse(template.render(context, request))
def gallery_l(request, query_term):
    query = get_object_or_404(SearchQuery, term=query_term)
    filelist = [f for f in listdir(settings.MEDIA_ROOT + query_term + '/edited') if isfile(join(settings.MEDIA_ROOT + query_term + '/edited', f))]
    template = loader.get_template('smartrez/gallery.html')
    context = {'query' : query, 'filelist' : filelist}
    return HttpResponse(template.render(context, request))