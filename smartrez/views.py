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
from shutil import copyfile
def q_create(request): # View is called from the first index page from the search button
  name = request.POST['term'].replace(' ','_').lower() #get search query from the POST request
  try:
   IS = ImageScraper()
   q = SearchQuery.objects.get(term=name) # check if we already have this query searched in the database
   thumb_list, img_list, pixabay_id = IS.get_img(srch = request.POST['term'], type= request.POST['type']) # from imagescraper get images for this query
   for img,thumb, id in itertools.zip_longest(img_list, thumb_list, pixabay_id):
    try:
     k = q.img_set.get(img_id = id)    # check the database with pixabay_id to see if it exists
    except:
     q.img_set.create(img_url = img, thumb_url = thumb, img_id = id) # if that errored, image didnt exist so create an entry for this supposedly newly added image on pixabay
  except: #in case its a new query, try would error so we come to except
   q = SearchQuery(term = name) # new searchquery with this new query name
   q.save()
   IS = ImageScraper()
   thumb_list, img_list, pixabay_id = IS.get_img(srch = request.POST['term'], type= request.POST['type']) # get images from pixabay
   for thumb, img, id in itertools.zip_longest(thumb_list, img_list, pixabay_id):
    q.img_set.create(img_url = img, thumb_url = thumb, img_id = id) #create img objects/database entries for images of this query
  return HttpResponseRedirect(reverse('smartrez:results', args = (name,))) #reverse smartrez:results with name as args and redirect to page, urls are namespaced with app name
def index(request): #view for the index page
 querylist = []
 for query in SearchQuery.objects.all():
  querylist.append(query.term) #load existing queries for the gallery view
 template = loader.get_template('smartrez/index.html')
 context = {'querylist' : querylist}
 return HttpResponse(template.render(context, request))
def results(request, query_term): #results page view
 query = get_object_or_404(SearchQuery,term=query_term) #get query
 template = loader.get_template('smartrez/results.html') #send query as context to the page, the page handles the rest
 context = {'query': query,'query_name' : query.term.replace('_',' ')}
 return HttpResponse(template.render(context, request))
def smartcrop(width, height, query_term, file): #function to run in threads to massively speed up operation time
    subprocess.run(['smartcrop --width %s --height %s "%s" "%s"' % (width, height, (settings.MEDIA_ROOT + query_term + '/edited/' + file), (settings.MEDIA_ROOT + query_term + '/edited/' + file))],shell=True)
    subprocess.run(['magick %s -compress JPEG -quality 80 %s' % ((settings.MEDIA_ROOT + query_term + '/edited/' + file), (settings.MEDIA_ROOT + query_term + '/edited/' + file))],shell=True)
def resize(request, query_term): #resize function
 query = get_object_or_404(SearchQuery,term=query_term)
 try:
     restorefilestring = request.POST['restore']
     restorefilelist = restorefilestring.split(',')
     restorelist = restorefilelist[:-1]
     if len(restorelist) > 0:
      for file in restorelist:
         copyfile(settings.MEDIA_ROOT + '%s/base/%s' % (query_term, file),settings.MEDIA_ROOT + '%s/edited/%s' % (query_term, file))
      template = loader.get_template('smartrez/gallery.html')
      filelist = [f for f in listdir(settings.MEDIA_ROOT + query_term + '/edited') if isfile(join(settings.MEDIA_ROOT + query_term + '/edited',f))]
      context = {'query': query, 'filelist': filelist, 'time' : int(round(time.time()))}  # sending list of filenames back to gallery so it can load pictures
      return HttpResponse(template.render(context, request))
 except:
  pass
 try:
     restorefilestring = request.POST['delete']
     restorefilelist = restorefilestring.split(',')
     restorelist = restorefilelist[:-1]
     if len(restorelist) > 0:
      for file in restorelist:
         os.remove(settings.MEDIA_ROOT + '%s/base/%s' % (query_term, file))
         os.remove(settings.MEDIA_ROOT + '%s/edited/%s' % (query_term, file))
      template = loader.get_template('smartrez/gallery.html')
      filelist = [f for f in listdir(settings.MEDIA_ROOT + query_term + '/edited') if isfile(join(settings.MEDIA_ROOT + query_term + '/edited',f))]
      context = {'query': query, 'filelist': filelist, 'time' : int(round(time.time()))}  # sending list of filenames back to gallery so it can load pictures
      return HttpResponse(template.render(context, request))
 except:
  pass
 ziph = zipfile.ZipFile(settings.MEDIA_ROOT + query_term + '.zip', 'w', zipfile.ZIP_DEFLATED)
 filestring = request.POST['act_img'] #get their selected images from POST
 filelist = filestring.split(',') #JS on the gallry page adds filename then a comma
 editlist = filelist [:-1] # last comma is a stray comma so remove last entry resulting from strip
 filelist = [f for f in listdir(settings.MEDIA_ROOT + query_term +'/edited') if isfile(join(settings.MEDIA_ROOT + query_term +'/edited', f))] #two directories, base and edited are maintained, editing will be handled in the edited folder, soon to add restoring base images into edited incase wrong operations
 real_imglist = []
 width = request.POST['width']
 height = request.POST['height']  #take dimensions from the POST requests, soon to be put as optional as more image ops are added
 threaddict = {}
 for counter, file in enumerate(editlist): #make and start threads
  threaddict[counter] = threading.Thread(target=smartcrop, args=(width, height,query.term,file))
  threaddict[counter].daemon = True
  threaddict[counter].start()
 for key in threaddict.keys(): #wait for all threads to finish
  threaddict[key].join()

 # for file in filelist:
 #         ziph.write(settings.MEDIA_ROOT + query_term +'/' +file, basename(settings.MEDIA_ROOT + query_term +'/' +file))
 # ziph.close() #this stuff is to be put into a download view
 print(filelist)
 template = loader.get_template('smartrez/gallery.html')
 context = {'query' : query, 'filelist' : filelist, 'time' : int(round(time.time()))} #sending list of filenames back to gallery so it can load pictures
 return HttpResponse(template.render(context, request))
def gallery(request, query_term): #gallery view, all submit buttons post to this view, so each image in the actimg post gets its use no. increased, will be moved to download view
    query = get_object_or_404(SearchQuery, term=query_term)
    urlstring = request.POST['act_img'] #same as the act img in resize
    urllist = urlstring.split(',')
    urllist = urllist[:-1]
    real_imglist = []
    for url in urllist:
        q_obj = query.img_set.get(thumb_url=url)
        q_obj.uses += 1
        q_obj.save()
        real_imglist.append(q_obj.img_url)
    IS = ImageScraper()
    filelist = IS.save_imgs(urllist=real_imglist, query_name=query.term) #call the image downloader with your selected urls
    template = loader.get_template('smartrez/gallery.html')
    context = {'query': query, 'filelist': filelist, 'time' : int(round(time.time()))}
    return HttpResponse(template.render(context, request))
def gallery_l(request, query_term): #gallery loader view
    query = get_object_or_404(SearchQuery, term=query_term) #normal gallery view takes POST requests, this does not, cause you wont post anything when you go to a gallery from the homepage
    filelist = [f for f in listdir(settings.MEDIA_ROOT + query_term + '/edited') if isfile(join(settings.MEDIA_ROOT + query_term + '/edited', f))]
    template = loader.get_template('smartrez/gallery.html')
    context = {'query' : query, 'filelist' : filelist, 'time' : int(round(time.time()))}
    return HttpResponse(template.render(context, request))