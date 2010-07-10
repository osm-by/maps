# -*- coding: utf-8 -*-
import urllib2
import os
import shutil

username = os.getusername()

dl_path = "/home/%s/.josm/bin/"%username
tile_cache = "/tmp/JMapViewerTiles_%s"%username
ram = "auto"   # may also be "512M" or any other value you want
clean_tile_cache = True 




java_options = "-Djava.net.preferIPv4Stack=true"
version_url = "http://josm.openstreetmap.de/latest"
mirror_url = "http://josm.openstreetmap.de/download/"
josm_filename = "josm-snapshot-%s.jar"

version_there = int(urllib2.urlopen(version_url).read())

file_here = dl_path+josm_filename%version_there
file_there = mirror_url+josm_filename%version_there

if clean_tile_cache:
  if os.path.exists(tile_cache):
    print "Cleaning up tile cache at %s"%tile_cache
    shutil.rmtree(tile_cache)

if not os.path.exists(file_here):
  if not os.path.exists(dl_path):
    print "Creating directory for downloaded josm builds"
    os.makedirs(dl_path)
    
  print "Downloading %s to %s"%(file_there, file_here)
  josm_contents = urllib2.urlopen(file_there).read()
  f = open(file_here, "wb")
  f.write(josm_contents)
  f.close()

if ram == "auto":
  try:
    import psutil
    fram = (psutil.avail_phymem()+psutil.avail_virtmem()/2)/1024/1024
    print "Free RAM: %sM" %(fram)
    ram = str(min(2048, fram))+"M"
  except ImportError:
    print "Can't import psutil - please install python-psutil or set 'ram' variable to fixed value."
    print "Using default of 256M"
    ram = "256M"


os.system ("java %s -Xms%s -Xmx%s -jar %s"%(
     java_options,
     ram, ram,
     file_here
))