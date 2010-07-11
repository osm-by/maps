#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from data1 import *

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8

try:
  import psyco
  psyco.full()
except ImportError:
  pass

points = [320719290, 767183490]


def main ():
  for point in points:
    print stops[point]["tags"].get("name", stops[point]["coord"])
    for pp in stops[point]["routes"]:
      print "   ", routes[pp]["tags"].get("name", None)
    for pp in stops[point]["neigh"]:
      print "      ", stops[pp]["tags"].get("name", stops[pp]["coord"])
  """
  Pass 1. Find routes with minimal number of changes.
  Dijkstra. Taken from wikipedia.
  """
  dst = {}
  prv = {}
  for route in routes:
    dst[route] = 1000000
    prv[route] = 0
  for route in stops[points[0]]["routes"]:
    dst[route] = 0
  Q = set(routes.keys())
  
  while Q:
    m = 10000000
    u = -1
    for k in Q:
      if dst[k] < m:
        m = dst[k]
        u = k

    # Here we could try dropping ways longer than already calculated
        
    if u == -1:
      print "Path not found :("
      exit()
    Q.remove(u)
    for v in routes[u]["neigh"]:
      alt = dst[u] + 1
      if alt < dst[v]:
        dst[v] = alt
        prv[v] = set([u])
      if alt == dst[v]:
        prv[v].add(u)
  # Going back


  
  m = 10000000
  u = -1
  
  for route in stops[points[1]]["routes"]:
    if m > dst[route]:
      m = dst[route]
      u = route
  print u, dst[u]
  s = [u]
  while prv[u]:
    u = prv[u].pop()  #TODO: multiple routes
    s.append(u)
  s.reverse()
  print s
  for route in s:
    print "%-10s  %-10s  %-10s  "%(

    routes[route]["tags"].get("ref", "XX"),
    routes[route]["tags"].get("name", "????"),
    route
    )
main()
