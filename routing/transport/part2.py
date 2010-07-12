#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
from data import *
from distance import Distance as dist

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

try:
  import psyco
  psyco.full()
except ImportError:
  pass


def main ():
  dist_matrix = {}
  t = len(stops)**2.
  d = 0
  for stop in stops.keys():
    stops[stop]["neigh"] = set([stop])
    stops[stop]["neigh_r"] = set(stops[stop]["routes"])
  for route in routes.keys():
    routes[route]["neigh"] = set()
  for k1, v1 in stops.iteritems():
    for k2, v2 in stops.iteritems():
      d += 1
      if d % 10000 == 0:
        print d / t
      if k1 > k2:
        if dist(stops[k1]["coord"],stops[k2]["coord"]) < 0.003:
          stops[k1]["neigh"].add(k2)
          stops[k2]["neigh"].add(k1)
          stops[k1]["neigh_r"].update(stops[k2]["routes"])
          stops[k2]["neigh_r"].update(stops[k1]["routes"])

  for k,v in stops.iteritems():
    fr_routes = stops[k]["routes"].copy()
    for neigh in stops[k]["neigh"]:
      fr_routes.update(stops[neigh]["routes"])
    for route in fr_routes:
      routes[route]["neigh"].update(fr_routes)

  for route in routes.values():
    print route["tags"].get("name", None), len(route["neigh"])
  ff = open("data1.py", "w")
  ff.write("stops = %s\n"%repr(stops))
  ff.write("routes = %s\n"%repr(routes))
  ff.write("routes_by_type = %s\n"%repr(routes_by_type))
  
  ff.close()  

  

main()
