import os
from os import listdir
from os.path import isfile, join

import threading
import subprocess
import sys
import requests

import urllib
from urllib.request import urlopen, urlretrieve
from django.conf import settings
from python_pixabay import Pixabay

from shutil import copyfile

class ImageScraper:
 def __init__(self):
  self.pix = Pixabay('5520434-306800159f2e30420f0743b5c')
 def get_img(self, srch, type):
  cis = self.pix.image_search(q=srch, lang='en', response_group='image_detals', image_type=type,orientation='horizontal',per_page='60') #api call
  thumbnail_list = []
  img_list = []
  pixabay_id = []
  for img in cis['hits']: #iter through items in the response
   thumbnail_list.append(img['previewURL']) #add the thumbnail ur;
   img_list.append(img['webformatURL']) #add the full res img url
   pixabay_id.append(img['id']) # add the id
  return thumbnail_list, img_list, pixabay_id #return the lists to the caller
 def save(self,query_name,url, name): #function to be used with threading to significantly speed up file saving processes
  try: #try-except in case there's a faulty url
   urllib.request.urlretrieve(url, settings.MEDIA_ROOT + '%s/base/%s' % (query_name, name))
   copyfile(settings.MEDIA_ROOT + '%s/base/%s' % (query_name, name),settings.MEDIA_ROOT + '%s/edited/%s' % (query_name, name))
  except:
   pass
 def save_imgs(self,urllist, query_name): # img download handling function
  if not os.path.exists(settings.MEDIA_ROOT + query_name): #make query, base and its edited folders
     os.makedirs(settings.MEDIA_ROOT + query_name)
  if not os.path.exists(settings.MEDIA_ROOT + query_name + '/' + 'base'):
      os.makedirs(settings.MEDIA_ROOT + query_name + '/' + 'base')
  if not os.path.exists(settings.MEDIA_ROOT + query_name + '/' + 'edited'):
      os.makedirs(settings.MEDIA_ROOT + query_name + '/' + 'edited')
  threaddict = {}
  for counter, url in enumerate(urllist): # make daemon threads and start them
    name = url.split('/')[len(url.split('/'))-1]
    #name = query_name + '_' + str(counter)
    threaddict[counter] = threading.Thread(target=self.save, args=(query_name, url,name))
    threaddict[counter].daemon = True
    threaddict[counter].start()
  for key in threaddict.keys(): #wait till all threads are done
   threaddict[key].join()
  onlyfiles = [f for f in listdir(settings.MEDIA_ROOT + query_name +'/edited') if isfile(join(settings.MEDIA_ROOT + query_name +'/edited', f))]
  #onlyfiles stores te filenames for files in edited directory of thr query so it can be then served in the webpage for the image selector in the gallery view
  return onlyfiles