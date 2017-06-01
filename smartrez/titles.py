import os
from os import listdir
from os.path import isfile, join
import subprocess
import sys
import requests
import bs4
from urllib.request import urlopen, urlretrieve 
import urllib
from django.conf import settings
from PIL import Image
from python_pixabay import Pixabay
import queue
import threading
import itertools
class ImageScraper:
 def __init__(self):
  self.pix = Pixabay('5520434-306800159f2e30420f0743b5c')
 def get_img(self, srch):
  cis = self.pix.image_search(q=srch, lang='en', response_group='image_detals', image_type='photo',orientation='horizontal',per_page='60')
  thumbnail_list = []
  img_list = []
  for img in cis['hits']:
   thumbnail_list.append(img['previewURL'])
   img_list.append(img['webformatURL'])
  return thumbnail_list, img_list
 def save(self,query_name,url, name, ext):
  try:
   urllib.request.urlretrieve(url, settings.MEDIA_ROOT + '%s/%s.%s' % (query_name, name, ext))
  except:
   pass
 def save_imgs(self,urllist, query_name):
  if not os.path.exists(settings.MEDIA_ROOT + query_name):
     os.makedirs(settings.MEDIA_ROOT + query_name)
  counter = 0
  threaddict = {}
  for url in urllist:
    splt = url.split('.')
    ext = splt[len(splt)-1]
    name = query_name + '_' + str(counter)
    threaddict[counter] = threading.Thread(target=self.save, args=(query_name, url,name,ext))
    threaddict[counter].daemon = True
    threaddict[counter].start()
    counter += 1
  threaddict[counter-1].join()
  counter = 0
  onlyfiles = [f for f in listdir(settings.MEDIA_ROOT + query_name) if isfile(join(settings.MEDIA_ROOT + query_name, f))]
  return onlyfiles