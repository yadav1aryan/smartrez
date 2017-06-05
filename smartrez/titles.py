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
  cis = self.pix.image_search(q=srch, lang='en', response_group='image_detals', image_type=type,orientation='horizontal',per_page='60')
  thumbnail_list = []
  img_list = []
  pixabay_id = []
  for img in cis['hits']:
   thumbnail_list.append(img['previewURL'])
   img_list.append(img['webformatURL'])
   pixabay_id.append(img['id'])
  return thumbnail_list, img_list, pixabay_id
 def save(self,query_name,url, name):
  try:
   urllib.request.urlretrieve(url, settings.MEDIA_ROOT + '%s/base/%s' % (query_name, name))
   copyfile(settings.MEDIA_ROOT + '%s/base/%s' % (query_name, name),settings.MEDIA_ROOT + '%s/edited/%s' % (query_name, name))
  except:
   pass
 def save_imgs(self,urllist, query_name):
  if not os.path.exists(settings.MEDIA_ROOT + query_name):
     os.makedirs(settings.MEDIA_ROOT + query_name)
  if not os.path.exists(settings.MEDIA_ROOT + query_name + '/' + 'base'):
      os.makedirs(settings.MEDIA_ROOT + query_name + '/' + 'base')
  if not os.path.exists(settings.MEDIA_ROOT + query_name + '/' + 'edited'):
      os.makedirs(settings.MEDIA_ROOT + query_name + '/' + 'edited')
  counter = 0
  threaddict = {}
  for url in urllist:
    name = url.split('/')[len(url.split('/'))-1]
    #name = query_name + '_' + str(counter)
    threaddict[counter] = threading.Thread(target=self.save, args=(query_name, url,name))
    threaddict[counter].daemon = True
    threaddict[counter].start()
    counter += 1
  for key in threaddict.keys():
   threaddict[key].join()
  onlyfiles = [f for f in listdir(settings.MEDIA_ROOT + query_name +'/edited') if isfile(join(settings.MEDIA_ROOT + query_name +'/edited', f))]
  return onlyfiles