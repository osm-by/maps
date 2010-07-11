#!/usr/bin/python
# -*- coding: utf-8 -*-


import math

#def Distance(t1, t2):
         #RADIUS = 6371 # earth's mean radius in km
         #p1=[0,0]
         #p2 = [0,0]
         #p1[0] = t1[0]*math.pi/180.
         #p1[1] = t1[1]*math.pi/180.
         #p2[0] = t2[0]*math.pi/180.
         #p2[1] = t2[1]*math.pi/180.

         #d_lat = (p2[0] - p1[0])
         #d_lon = (p2[1] - p1[1])
         
         #a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(p1[0]) * math.cos(p2[0]) * math.sin(d_lon/2) * math.sin(d_lon/2)
         ##print a, 1-a, p1, p2
         #c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
         #d = RADIUS * c
         #return d

Distance = lambda p1, p2: math.sqrt( (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 )
