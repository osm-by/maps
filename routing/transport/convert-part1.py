#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import bz2
from lxml import etree

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8 

try:
  import psyco
  psyco.full()
except ImportError:
  pass


def main ():


  print sys.argv[1]
  
  """
  Pass 1: Route relation -> dict
  """
  print "Pass 1."
  NODES_READ = 0
  WAYS_READ = 0
  tags = {}
  routes_by_type = {}
  routes = {}
  members = {}
  members["way"] = []
  members["node"] = []
  add_later = {}
  add_later["way"] = set()
  add_later["node"] = set()
  stops = {}
  osm_infile = bz2.BZ2File(sys.argv[1], "rb")
  context = etree.iterparse(osm_infile)
  for action, elem in context:
    items = dict(elem.items())
    if elem.tag == "node":
      NODES_READ += 1
      if NODES_READ % 10000 == 0:
        print "Nodes read:", NODES_READ
      tags = {}
    elif elem.tag == "member":
      if items["type"] in members:
        members[items["type"]].append((int(items["ref"]),items["role"]))
        add_later[items["type"]].add(int(items["ref"]))
    elif elem.tag == "tag":
      tags[items["k"]] = items["v"]
    elif elem.tag == "way":
      tags = {}
    elif elem.tag == "relation":
      if tags.get("type",None) == "route":
        if "route" in tags:
          if tags["route"] not in routes_by_type:
            routes_by_type[tags["route"]] = set()
          routes[int(items["id"])] = {"tags":tags, "members":members}
          routes_by_type[tags["route"]].add(int(items["id"]))
          for node in members["node"]:
            if "stop" in node[1]:
              if node[0] not in stops:
                stops[node[0]] = {}
                stops[node[0]]["routes"] = set()
              stops[node[0]]["routes"].add(int(items["id"]))

      members = {}
      members["way"] = []
      members["node"] = []
      tags = {}
    elem.clear()
  """
  Pass 2: reading needed nodes
  """
  print "Pass 2."
  NODES_READ = 0
  WAYS_READ = 0
  tags = {}
  osm_infile = bz2.BZ2File(sys.argv[1], "rb")
  context = etree.iterparse(osm_infile)
  for action, elem in context:
    items = dict(elem.items())
    if elem.tag == "node":
      NODES_READ += 1
      if NODES_READ % 10000 == 0:
        print "Nodes read:", NODES_READ

      if int(items["id"]) in stops:
        stops[int(items["id"])]["tags"] = tags
        stops[int(items["id"])]["coord"] = (float(items["lon"]),float(items["lon"]))
      tags = {}
      try:
        add_later["node"].remove(int(items["id"]))
      except KeyError:
        "okay, np - node wasn't intersting anyway"
    elif elem.tag == "tag":
      tags[items["k"]] = items["v"]
    elif elem.tag == "way":
      # TODO: read also ways
      tags = {}
    elif elem.tag == "relation":
      tags = {}
    elem.clear()


  ff = open("data.py", "w")
  ff.write("stops = %s\n"%repr(stops))
  ff.write("routes = %s\n"%repr(routes))
  ff.write("routes_by_type = %s\n"%repr(routes_by_type))
  ff.close()
  
  print "Number of not found interesting nodes: %s" % len(add_later["node"])
  print "Number of stops found: %s" % len(stops)
  print "Number of routes found: %s" % len(routes)
  print "Number of route types found: %s" % len(routes_by_type)
main()
