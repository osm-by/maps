#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import sys
import cgi
import math
from xml.sax import make_parser, handler
from pngcanvas import PNGCanvas
import gettext

trans = gettext.GNUTranslations(open("%s/i18n/%s.mo" % (sys.path[0],sys.argv[1])))
_ = trans.gettext

from  calchome_xyn import calcHome
import xml
import datetime
import time
import tagChecker
from osm_micro_tools import *
from xml.utils.iso8601 import parse



class osmParser(handler.ContentHandler):
  def __init__(self, filename):
    #self.db = db
    self.useless = ('',
      'created_by',
      'source',
      'editor',
      'ele',
      'time',
      'editor',
      'author',
      'hdop',
      'pdop',
      'sat',
      'speed',
      'fix',
      'course',
      'converted_by',
      'attribution',
      'upload_tag',
      'history')
    self.User = {}
    self.currentId = 0
    self.goodUser = ('')
    self.TilesCreated = 0
    self.Nodes = {}
    self.NodesToWays = {}
    self.NodesToWaysR = {}
    self.Ways = {}
    self.Borders = {}
    self.Places = {}
    self.DatesGraph = {}
    self.RoutableWays = []
    self.BPlaces = {}
    self.currentUser = ""            # user who created latest obj
    self.currentType = ""            # latest obj type
    self.NodesCount = 0
    self.PlacesCount = 0
    self.RelationsCount = 0
    self.Address = {}
    self.currentMembers = []
    self.currentRelID = 0
    self.WaysCount = 0
    self.prompt = 10000
    self.BorderList = []
    self.BordersCount = 0
    self.MinLaTile = 1000000
    self.MaxLaTile = 0
    self.MinLoTile = 1000000
    self.MaxLoTile = 0
    self.FillTile = 0
    self.TagsList = {}
    self.ZoomLevel = 200.0  #130
    self.Tiles = {}
    self.FixMe = _('<b>FixMe</b>')
    self.AddrRelLinks = ''
    self.MaxTagsElems = 20
    self.LastChange = ''
    self.FirstChange = 'z'
    self.WaysPassed = []
    self.CountryName = sys.argv[2]                            # Second argument - Country name
    self.DoRouting = True
    if sys.argv[3] == "norouting":
      self.DoRouting = False


    htmlheader = "<html><head><title>%%s%s %s: %%s</title><meta http-equiv=Content-Type content=\"text/html; charset=UTF-8\" /><script src=\"http://me.komzpa.net/sorttable.js\"></script></head><body>" % (_("OSM Stats"),self.CountryName)
    htmltablestart = "<table class=\"sortable\" sytle=\"width: 100%; border: 1px solid gray\" border=1 width=100%>"
    def htmltablerow (cols):
        tr = "<tr>"
        for col in cols:
	  if type(col) == type(float()):
	    tr = tr + "<td align=\"right\">%.3f</td>" % (col,)
	  else:
	    tr = tr + "<td>%s</td>" % (col,)
        return tr+"</tr>"
    self.warningsFile = open('warnings.html','w')
    self.warningsFile.write(htmlheader % (" ", _("Warnings")))
    self.warningsFile.write(htmltablestart);
    self.warningsFile.write(htmltablerow((_("Warning type"), _("Way"))))
    try:
      parser = make_parser()
      parser.setContentHandler(self)
      parser.parse(filename)
    except xml.sax._exceptions.SAXParseException:
      sys.stderr.write( _("Error loading %s\n") % filename)



## Dealing with BorderList
    self.BorderList.sort((lambda x,y: int((y[0]-x[0])*100000)))
    
    self.unnamedBordersFile = open('unnamed.html','w')


    in_unnamed = 0
    in_named = 0
    perpage = 500
    for tt in self.BorderList:

           dens, area, nodesInWay, bbox = tt



           if (in_unnamed%perpage)==0:
                 self.unnamedBordersFile.write('</table></body></html>')
                 self.unnamedBordersFile.close()
                 self.unnamedBordersFile = open('unnamed%s.html'%(int(in_unnamed/perpage)+1),'w')
                 self.unnamedBordersFile.write(htmlheader % (" ", _("Unnamed borders")) )
                 self.unnamedBordersFile.write(htmltablestart)
                 self.unnamedBordersFile.write(htmltablerow(( _("Area [km<sup>2</sup>]"),_("Nodes"),_("Density [nodes/km<sup>2</sup>]"),_("Link"))))
                 in_unnamed += 1
           bf = self.unnamedBordersFile
           bf.write(htmltablerow((area,  nodesInWay, dens,  linkBbox(bbox))))
    self.unnamedBordersFile.write('</table></body></html>')
    self.unnamedBordersFile.close()


    filename = open('unnamed.html','w')
    filename.write(htmlheader % (" ", _("Unnamed borders pages list")) )
    filename.write("<body><h2>%s</h2><ul>" % _("Unnamed borders pages list"))
    for i in range(1,int(in_unnamed/perpage)+2):
      filename.write('<li><a href=unnamed%s.html>%s %s</a>'%(i,_("Page"),i))
    filename.write("</ul></body></html>")
    filename.close()





    dirname = "addr"
    if not os.path.isdir("./" + dirname + "/"):
      os.mkdir("./" + dirname + "/")
    filename = open('addr/index.html','w')
    filesStarted = ['addr/index.html']
    filename.write(htmlheader % (" ", _("Postal address relations")) )
    def AddrTreeRecurse (top, wayback="» "):

      if top in self.WaysPassed:
        self.warningsFile.write (htmltablerow((_("double-pass on address relation"),top)))
        return
      wayback = wayback + "%s<a href=%s.html>%s</a> » " % (linkRelationIcon(top),top, self.Address[top]["tags"].get("name",top) )
      filename = open('addr/%s.html'%(top,),'w')
      filename.write(htmlheader % ("", self.Address[top]["tags"].get("name", "Unknown address")))
      filename.write(" %s<p>" % wayback)
      nodes = 0
      ways = 0
      rels = 0
      self.WaysPassed.append(top)
      for ctype, child in self.Address[top]["child"]:
       if ctype == 'node':
         if nodes == 0:
           filename.write(htmltablestart)
           filename.write(htmltablerow((_("Name"),_("Density"),_("Area"),_("Nodes"),_("Type"),_("Link"))))
         nodes += 1
         if int(child) in self.BPlaces:
           area,nodesIn, bbox, tags = self.BPlaces[int(child)]
           filename.write(htmltablerow((\
            tags["name"], \
            1.* nodesIn / area, \
            area, \
            nodesIn, \
            tags["place"], \
            linkBboxMarker(bbox, (tags["lat"],tags["lon"])), \
            )))
         elif int(child) in self.Places:
           filename.write(htmltablerow((\
            self.Places[int(child)].get("name", child), \
            " ", \
            " ", \
            " ", \
            self.Places[int(child)].get("place", _("??? unknown")), \
            linkNode(child), \
            )))
         else:
           filename.write(htmltablerow((linkNode(child),) ))
      filename.write("</table>")
      for ctype, child in self.Address[top]["child"]:
       if ctype == 'way':
         filename.write(linkWay(child))
      for ctype, child in self.Address[top]["child"]:
       if ctype == 'relation':
         if rels == 0:
           filename.write(_("<h3>Relations</h3>"))
         rels += 1
         if child in self.Address:
           filename.write("<br>%s<a href=%s.html>%s</a> " %(linkRelationIcon(child),child, self.Address[child]["tags"].get("name",child) ))
           AddrTreeRecurse(child,wayback)
         else:
           filename.write(linkRelation(child))
    


      #print self.BPlaces
      ##filename.write(str(self.Address[top]["child"]))
      filename.write("</body></html>")
      filename.close()





    while self.Address:
      top = self.Address.keys()[0]
      while self.Address[top]["parent"] in self.Address:
        top = self.Address[top]["parent"]
      AddrTreeRecurse (top)
      filename.write("<a href=%s.html>%s</a> " %(top, self.Address[top]["tags"].get("name",top) ))
      self.AddrRelLinks = self.AddrRelLinks + "<a href=addr/%s.html>%s</a> " %(top, self.Address[top]["tags"].get("name",top) )
      #print self.Address[top]
      for aaaaa in self.Address.keys():
        del self.Address[aaaaa]

    filename.close()




    for toClose in filesStarted:
      filename = open(toClose,'a')
      filename.write("</body></html>")
      filename.close()









    filename = open("tags.html",'w')

    taglist = self.TagsList.keys()
    taglist.sort()
    alphabet = []
    for k in taglist:
     filename.close()
     alpha = k[0]
     if alpha not in ("a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"):
	alpha = "other"
	tt = _("other")
     if alpha not in alphabet:
	alphabet.append(alpha)
	filename = open("tags-%s.html"%(alpha,),'w')
	filename.write(htmlheader % ("[%s]" % _(alpha), _("Tags")))
	filename.write("""
<script type="text/javascript">
var d = document;
var offsetfromcursorY=15 // y offset of tooltip
var ie=d.all && !window.opera;
var ns6=d.getElementById && !d.all;
var tipobj,op=0;
function tt(el,txt) { if (d.getElementById('mess').style.visibility=='hidden'){	tipobj=d.getElementById('mess');
	e = el;	tipobj.innerHTML = '<div style="float:right;align:right;cursor:pointer;cursor:hand;border-bottom:1px solid grey;padding:2px;border-left:1px solid black;" onclick="hide_info(this)">x</div>'+ txt;	el.onmousemove=positiontip;};}

function hide_info(el) {op=0;tipobj.style.opacity = op; d.getElementById('mess').style.visibility='hidden';}

function ietruebody(){return (d.compatMode && d.compatMode!="BackCompat")? d.documentElement : d.body}

function positiontip(e) { if (d.getElementById('mess').style.visibility=='hidden'){
	var curX=(ns6)?e.pageX : event.clientX+ietruebody().scrollLeft;
	var curY=(ns6)?e.pageY : event.clientY+ietruebody().scrollTop;
	var winwidth=ie? ietruebody().clientWidth : window.innerWidth-20
	var winheight=ie? ietruebody().clientHeight : window.innerHeight-20
	var rightedge=ie? winwidth-event.clientX : winwidth-e.clientX;
	var bottomedge=ie? winheight-event.clientY-offsetfromcursorY : winheight-e.clientY-offsetfromcursorY;
	if (rightedge < tipobj.offsetWidth)	tipobj.style.left=curX-tipobj.offsetWidth+"px";
	else tipobj.style.left=curX+"px";
	if (bottomedge < tipobj.offsetHeight) tipobj.style.top=curY-tipobj.offsetHeight-offsetfromcursorY+"px"
	else tipobj.style.top=curY+offsetfromcursorY+"px";};}
function ap(el) {el.onmousemove='';op=tipobj.style.opacity;if (op==0){	op = 1;	tipobj.style.opacity = op; tipobj.style.visibility="visible";};
if(op < 1) {op += 0.1;	tipobj.style.opacity = op;tipobj.style.filter = 'alpha(opacity='+op*100+')';t = setTimeout('appear()', 30);};}</script>

<style>span{cursor:pointer;cursor:hand;} span:hover{color:navy}</style>
</head><body><div id="mess" style="visibility: hidden;position:absolute;background-color:white; border:1px dotted red; width:350px; "></div><table class="sortable" sytle="width: 100%; border: 1px solid gray" border=1 width=100%>
<tr><td>k<td>num<td>v's""")
     else:
	filename = open("tags-%s.html"%(alpha,),'a')
     filename.write( "<tr><td>%s<td>%s<td>" % \
      (k, self.TagsList[k][1] ))


     vallist = self.TagsList[k].keys()
     vallist.sort()
     for v in vallist:
      if v is not 1:
       uslist = self.TagsList[k][v].keys()
       uslist.sort()
       z = " "
       if self.MaxTagsElems > len(self.TagsList[k][v][objN("way")]):
	if self.TagsList[k][v][objN("way")]:
	    z = z + _("Ways: ")
	for p in self.TagsList[k][v][objN("way")]:
	    z = z + linkWay(p)+" "
       if self.MaxTagsElems > len(self.TagsList[k][v][objN("node")]):
	if self.TagsList[k][v][objN("node")]:
	    z = z +"<br>"+ _("Nodes: ")
	for p in self.TagsList[k][v][objN("node")]:
	    z = z + linkNode(p)+" "
       if self.MaxTagsElems > len(self.TagsList[k][v][objN("relation")]):
	if self.TagsList[k][v][objN("relation")]:
	    z = z + "<br>"+_("Relations: ")
	for p in self.TagsList[k][v][objN("relation")]:
	    z = z + linkRelation(p)+" "
       for p in uslist:
         if p not in (1, 2, 3, 5):
          z = z + "<br>%s: %s "% (linkUser(self.User[p]["Name"]), self.TagsList[k][v][p])
       filename.write( """<span onmouseover="tt(this,'%s<br>')" onclick="ap(this)">%s (%s)</span>, """ % \
        (z, v, self.TagsList[k][v][1] ))
    filename.close()
    for alpha in alphabet:
      filename = open("tags-%s.html"%(alpha,),'a')
      filename.write("</table>")
      for link in alphabet:
	filename.write("\n<a href=tags-%s.html> %s </a>| " % (link,_(link)))
      filename.write("</body></html>")
    filename.close()
    
    kml = open('users.kml','w')
    kml.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<kml xmlns="http://earth.google.com/kml/2.0">
<Document>
<Style id="rss">
<IconStyle>
<scale>0.5</scale>
<Icon>
<href>http://komzpa.net/favicon.ico</href>
</Icon>
</IconStyle>
</Style>
<Folder>""")
    kml.write("<name>%s users</name>" % (self.CountryName) )
    usersFile = open('users.html','w')
    usersFile.write(htmlheader % (" ",_("Users")))
    usersFile.write(htmltablestart)
    usersFile.write(htmltablerow((_("User"), _("Nodes"), _("Ways"), _("Relations"), _("%"), _("Speed [obj/day]"), _("First known edit"), _("Latest known edit"), _("Links"))))
    userlist = self.User.keys()
    userlist.sort(lambda x,y: self.User[y]["Nodes"]-self.User[x]["Nodes"])
    for user in self.User.values():
	if user["LastDate"] > self.LastChange:
	  self.LastChange = user["LastDate"]
    ttt = """<Placemark>
<name>%s</name>
<description>&lt;h2&gt;&lt;a href=&quot;http://openstreetmap.org/user/%s&quot;&gt;%s&lt;/a&gt;&lt;/h2&gt;&lt;br&gt;
Nodes: %s Ways: %s Relations: %s Since: %s

</description>
<styleUrl>#rss</styleUrl>
<Point><coordinates>%s, %s</coordinates></Point>
</Placemark>"""
	
    for user in userlist:
	if self.FirstChange > self.User[user]["FirstDate"]:
	    self.FirstChange =  self.User[user]["FirstDate"]
	CSList = []
	for i in self.User[user]["changesets"].values():
	  CSList.append([i["lat"],i["lon"],i["num"]])
	CHLink = "&nbsp;"
	if CSList:
	 lat, lon = tuple(calcHome(CSList))
	 escapedName = cgi.escape (self.User[user]["Name"])
         CHLink = "<a href=\"http://openstreetmap.org/?mlat=%f&mlon=%f&minlat=%s&minlon=%s&maxlat=%s&maxlon=%s&box=yes\">%s</a>" % \
		      (lat, lon, self.User[user]["minlat"], self.User[user]["minlon"], self.User[user]["maxlat"], self.User[user]["maxlon"], _("CalcedHome"))
	 kml.write(ttt % (escapedName, escapedName, escapedName, self.User[user]["Nodes"], \
		 self.User[user]["Ways"], \
		 self.User[user]["Relations"], \
		 self.User[user]["FirstDate"], \
		 lon, lat) )
	speed = ((self.User[user]["Nodes"]+self.User[user]["Ways"]+self.User[user]["Relations"])/(parse(self.LastChange)-parse(self.User[user]["FirstDate"])+1))*86400


        usersFile.write(htmltablerow(((linkUser(self.User[user]["Name"]), \
		 self.User[user]["Nodes"], \
		 self.User[user]["Ways"], \
		 self.User[user]["Relations"], \
		 100. * (1.* self.User[user]["Nodes"]  / self.NodesCount +  1. *  self.User[user]["Ways"] / self.WaysCount) / 2,\
		 speed,\
		 self.User[user]["FirstDate"], \
		 self.User[user]["LastDate"], \
		 CHLink 
		 , \
))))
    kml.write("""</Folder>
</Document>
</kml>""")
    kml.close()
    usersFile.write( "</table></body></html>")
    usersFile.close()

    localLangs = _("name:be,name:en,name:ru")
    localLangs = localLangs.split(",")
    localLangs = tuple (localLangs)
    
    pointsFile = open('points.html','w')
    pointsFile.write(htmlheader % ("",_("Localities")))
    pointsFile.write(htmltablestart)
    pointsFile.write(htmltablerow((_("Name"),) + localLangs + ( _("Type"), _("Link"))))
    for PointNum in self.Places.keys():
      place = self.Places[PointNum]
      localLangsT = []
      for langtag in localLangs:
	localLangsT.append(place.get(langtag, self.FixMe))
      localLangsT = tuple (localLangsT)
      pointsFile.write(htmltablerow(
      (place.get("name",self.FixMe),\
        ) + localLangsT +  ( \
       place['place'], linkMarker(place['lat'], place['lon'], _("goto") ) ) ))
    pointsFile.write( "</table></body></html>")
    pointsFile.close()



    indexFile = open('index.html','w')
    indexFile.write(htmlheader % (_("Welcome to :"),""))
    indexFile.write(_("<h3>OSM Statistics for %s</h3>") % self.CountryName)
    indexFile.write("<ul>")
    indexFile.write(_("<li><a href=users.html>users</a></li>"))
    indexFile.write(_("<li><a href=points.html>points</a></li>"))
    indexFile.write(_("<li>address relations: %s</li>") % self.AddrRelLinks )
    indexFile.write(_("<li><a href=warnings.html>warnings</a></li>"))
    indexFile.write(_("<li><a href=borders.html>borders</a></li>"))
    indexFile.write(_("<li><a href=unnamed.html>unnamed borders</a></li>"))
    if self.DoRouting:
      indexFile.write(_("<li><a href=route.html>routing subgraphs</a></li>"))
    indexFile.write(_("<li>tags: "))
    for alpha in alphabet:
     indexFile.write("\n<a href=tags-%s.html>%s</a> | " % (alpha,_(alpha)))
    indexFile.write( """</ul>
<a href=density.png><img src="density.png" width=100%></a>
""")


    best = (0,0)
    for i in self.Tiles.keys():
      for j in self.Tiles[i].keys():
        if len(self.Tiles[i][j]) > self.FillTile:
          self.FillTile = len(self.Tiles[i][j])
	  best = (i,j)


    self.DatesCSV = open('graph.csv','w')
    daysSorted = self.DatesGraph.keys()
    daysSorted.sort()
    for day in daysSorted:
      self.DatesCSV.write("%s\t%s\t%s\t%s\n"%(day,self.DatesGraph[day][0],self.DatesGraph[day][1],self.DatesGraph[day][2]) )
    self.DatesCSV.close()
    
    
    
    speed = (self.NodesCount+self.WaysCount+self.RelationsCount)/(parse(self.LastChange)-parse(self.FirstChange))*86400
    indexFile.write( _("<p>Average mapping speed: <b>%f</b> obj/day</p>") % (speed, ))
    indexFile.write( _("<p>Tiles fill(avg/max): <b>%f</b>/<b>%s</b></p>") % (self.NodesCount/(self.TilesCreated*1.),self.FillTile, ))
    indexFile.write( _("<p>Number of Nodes: <b>%s</b></p>") % (self.NodesCount, ))
    indexFile.write( _("<p>Number of Ways: <b>%s</b></p>") % (self.WaysCount, ))
    indexFile.write( _("<p>Number of Relations: <b>%s</b></p>") % (self.RelationsCount, ))
    indexFile.write( _("<p>Number of Borders/Places: <b>%s</b>/<b>%s</b></p>") % (self.BordersCount, self.PlacesCount))
    indexFile.write( _("<p>First known update: <b>%s</b></p>") % (self.FirstChange, ))
    indexFile.write( _("<p>Last update: <b>%s</b></p>") % (self.LastChange, ))
    indexFile.write("</body></html>")
    indexFile.close()
 
    filename = open('oneline.inc.html','w')
    filename.write("%s</a><td>%s</td><td>%s</td><td>%.3f</td><td>%.3f</td><td>%s</td></tr>" % (self.CountryName, self.LastChange, len(self.User), speed, \
         self.NodesCount/(self.TilesCreated*1.),\
         linkBbox((best[0]/self.ZoomLevel,best[1]/self.ZoomLevel,(best[0]+1)/self.ZoomLevel,(best[1]+1)/self.ZoomLevel), box = "no", text = self.FillTile), \
))
    filename.close()

### Making routing
    if self.DoRouting:
      self.warningsFile = open('route.html','w')
      self.warningsFile.write(htmlheader % ("",_("Routes")))
      self.warningsFile.write(htmltablestart)
      self.warningsFile.write(htmltablerow((_("Number of ways"),_("First way in group"))))




      wayQ = []
      wayP = []
      numRoute = 0
      self.WayGroups = {0:"",}
      self.WayGroupsId = {0:"",}
      numR = len(self.RoutableWays)
      numP = 0
      numPrev = 0
      starttime = time.time()
      prevtime = starttime
      while self.RoutableWays:
	if time.time()-prevtime >= 6:
	  print "still %s %s, %s, %s%%, ETA:%ss (%s/s)"%(len(wayQ),numP, numR-numP, 1.*numP/numR*100., (numR-numP)*(time.time()-prevtime)/(numP-numPrev),   (numP-numPrev)/(time.time()-prevtime))
	  prevtime=time.time()
	  time.sleep(1)

	  numPrev = numP
	if not wayQ:
	  wayQ.append(self.RoutableWays.pop())
	  wayP.reverse()
	  wayP.extend(wayQ)
	  wayP.reverse()
	  print "NewRoutable", numRoute
	  numRoute += 1
	  self.WayGroups[numRoute] = 1
	  self.WayGroupsId[numRoute] = wayQ[0]

	way = self.Ways[wayQ.pop()]
	#print way, wayQ
	for node in way:

	  if len(self.NodesToWays[node]) != 1:
	   for tway in self.NodesToWays[node]:
	    if tway not in wayP:
	      if tway in self.RoutableWays:
		wayQ.append(tway)
		wayP.reverse()
		wayP.append(tway)
		wayP.reverse()
		self.WayGroups[numRoute] += 1
		self.RoutableWays.remove(tway)
	numP += 1
      print  self.WayGroups
      for i in range(1,numRoute):
	self.warningsFile.write(htmltablerow((self.WayGroups[i],linkWayMap(self.WayGroupsId[i]))))


## Making pretty image
    density = self.NodesCount/self.TilesCreated*1.
    sys.stderr.write('Generating picture')
    png = PNGCanvas(self.MaxLoTile-self.MinLoTile,self.MaxLaTile-self.MinLaTile+1)
    gamma=0.5

#    for i in self.Tiles.keys():
#      for j in self.Tiles[i].keys():
#        if len(self.Tiles[i][j]) > self.FillTile:
#          self.FillTile = len(self.Tiles[i][j])

    for i in self.Tiles.keys():
      for j in self.Tiles[i].keys():
        c = len(self.Tiles[i][j])*1./self.FillTile
        c = c**gamma

        t = int(c*255)
        png.point(j-self.MinLoTile,-i+self.MaxLaTile,[256-t,256-t,t,0xFF])
    for i in range(0, png.width+1):
        c = i/(png.width+1*1.)
	#c = math.log(c+1)
        c = c**gamma
        t = int(c*255)
        png.point(i,png.height-1,[256-t,256-t,t,0xFF])
   



    filename = open("density.png",'wb')
    filename.write(png.dump())
    filename.close()
    sys.stderr.write('.\n')

    self.warningsFile.write('</table></body></html>')
    self.warningsFile.close()






  def UserTasks(self, uID, uName, uDate):
    if uID not in self.User:
      self.User[uID] = {"Name": uName, \
			"Ways": 0, \
			"Nodes": 0,\
			"Relations": 0,\
			"FirstDate": uDate,\
			"LastDate": uDate,\
			"lat": 0,\
			"lon": 0,\
			"minlat": 9999,\
			"minlon": 9999,\
			"maxlat": 0,\
			"maxlon": 0,\
			"changesets": {},\
		  }
    if self.User[uID]["FirstDate"] > uDate:
      self.User[uID]["FirstDate"] = uDate
    if self.User[uID]["LastDate"] < uDate:
      self.User[uID]["LastDate"] = uDate


  def UserLatLon(self, uid, cset, lat, lon):

    
    if cset not in self.User[uid]["changesets"]:
     self.User[uid]["changesets"][cset] = {"lat":0,"lon":0,"num":0}
    self.User[uid]["changesets"][cset]["lat"] = (self.User[uid]["changesets"][cset]["lat"] * self.User[uid]["changesets"][cset]["num"] + float(lat))/(self.User[uid]["changesets"][cset]["num"]+1)
    self.User[uid]["changesets"][cset]["lon"] = (self.User[uid]["changesets"][cset]["lon"] * self.User[uid]["changesets"][cset]["num"] + float(lon))/(self.User[uid]["changesets"][cset]["num"]+1)
    self.User[uid]["changesets"][cset]["num"] += 1

    if lat > self.User[uid]["maxlat"]:
      self.User[uid]["maxlat"] = lat
    if lon > self.User[uid]["maxlon"]:
      self.User[uid]["maxlon"] = lon
    if lat < self.User[uid]["minlat"]:
      self.User[uid]["minlat"] = lat
    if lon < self.User[uid]["minlon"]:
      self.User[uid]["minlon"] = lon


    self.User[uid]["Nodes"] += 1

  def startElement(self, name, attrs):
    """Handle XML elements"""
    if name in('node','way','relation'):
      self.currentType = name
      self.currentId = int(attrs.get('id'))
      self.tags = {}
      self.isInteresting = False
      self.waynodes = []
      self.useTiles=0
      uid=attrs.get('uid',attrs.get("user",""))
      self.currentUser = uid
      date = attrs.get('timestamp')
      self.UserTasks(uid, attrs.get('user',""), date)
      day = date[0:10]
      hour = date[0:15]
      changeset = attrs.get("changeset", hour)
      if day not in self.DatesGraph:
       self.DatesGraph[day] = [0,0,0]
      


      if name == 'node':
        self.DatesGraph[day][0] += 1
        id = int(attrs.get('id'))
        self.nodeID = id
        lat = float(attrs.get('lat'))
        lon = float(attrs.get('lon'))
	self.UserLatLon(uid,changeset,lat,lon)
        self.Nodes[id] = (lat,lon)
        tilelat = int(lat*self.ZoomLevel)
        tilelon = int(lon*self.ZoomLevel)
        if tilelat<self.MinLaTile:
          self.MinLaTile = tilelat
        if tilelat>self.MaxLaTile:
          self.MaxLaTile = tilelat
        if tilelon<self.MinLoTile:
          self.MinLoTile = tilelon
        if tilelon>self.MaxLoTile:
          self.MaxLoTile = tilelon

        if tilelat in self.Tiles:
            if tilelon in self.Tiles[tilelat]:
              self.Tiles[tilelat][tilelon].append(id)
            else:
              self.Tiles[tilelat][tilelon] = [id,]
              self.TilesCreated += 1
        else:
    	    self.Tiles[tilelat] = {}
    	    self.Tiles[tilelat][tilelon] = [id,]
    	    self.TilesCreated += 1
        self.tags['lat'] = lat
        self.tags['lon'] = lon
        self.NodesCount += 1
        self.prompt -= 1
        if(not self.prompt):
         self.prompt = 10000
         sys.stderr.write( "%1.3fM nodes (%s tiles, %.4f nodes per tile) \n" % (float(self.NodesCount) / 1000000.0, self.TilesCreated, self.NodesCount/(self.TilesCreated*1.)))
        self.currentUser = uid


      elif name == 'way':
        self.DatesGraph[day][1] += 1
        id = int(attrs.get('id'))
        self.WayID = id
        self.WaysCount += 1

        self.User[uid]["Ways"] += 1
        self.prompt -= 1
	self.LastChange = attrs.get('timestamp')
        if(not self.prompt):
         self.prompt = 1000
         sys.stderr.write( "%1.3fM ways (%s borders)\n" % (float(self.WaysCount) / 1000000.0, self.BordersCount))
      elif name == 'relation':
        self.DatesGraph[day][2] += 1
	self.currentMembers = []
        self.User[uid]["Relations"] += 1
	self.RelationsCount += 1
	self.currentRelID = attrs.get('id')
    elif name == 'nd':
       """Nodes within a way -- add them to a list"""
       node = int(attrs.get('ref'))
       self.waynodes.append(node)
    elif name == 'member':
      """Members of relation"""
      mtype, mref, mrole = (attrs.get('type'),attrs.get('ref'), attrs.get('role'))
      self.currentMembers.append (((mtype, mref), mrole))

    elif name == 'tag':
      """Tags - store them in a hash"""
      k,v = (attrs.get('k'), attrs.get('v'))

      # Test if a tag is interesting enough to make it worth
      # storing this node as a special "point of interest"
      #if k in ('boundary', 'admin_level', 'place','name','name:ru','name:be','name:en','border_type','highway'):
      self.tags[k] = v
      #   self.isInteresting = True
      if not tagChecker.TagIsAllowed(k):
	if k not in self.TagsList:
	  self.TagsList[k] = {}
	  self.TagsList[k][1]=1
	else:
	  self.TagsList[k][1] += 1

	if v in self.TagsList[k]:
	  self.TagsList[k][v][1] += 1
	else:
	  self.TagsList[k][v] = {}
	  self.TagsList[k][v][1] = 1
	  self.TagsList[k][v][objN("way")] = []
	  self.TagsList[k][v][objN("node")] = []
	  self.TagsList[k][v][objN("allother")] = []
	if self.currentUser in self.TagsList[k][v]:
	  self.TagsList[k][v][self.currentUser] += 1
	else:
	  self.TagsList[k][v][self.currentUser] = 1
        self.TagsList[k][v][objN(self.currentType)].append(self.currentId)  #################


  def endElement(self, name):
    if name == 'way':
      id=self.WayID
      if self.DoRouting:
	for i in self.waynodes:
	  if i not in self.NodesToWays:
	    self.NodesToWays[i] = []
	  self.NodesToWays[i].append(id)
	if 'highway' in self.tags:
	  if self.tags['highway'] not in ('footway','path','pedestrain'):
		  self.RoutableWays.append(id)
	self.Ways[id] = self.waynodes
      #if self.isInteresting:
      if 'boundary' in self.tags and 'admin_level' in self.tags:                          ###### boundaries
        if self.tags['boundary']=='administrative' and self.tags['admin_level']=='8':
         self.BordersCount += 1
         if self.waynodes[0] == self.waynodes[-1]:
           minlat,minlon,maxlat,maxlon = (400,400,-400,-400)
           boundary = []
           for i in self.waynodes:
            if i in self.Nodes:
             lat,lon = self.Nodes[i]
             boundary.append((lat,lon))
             if lat>maxlat:
                maxlat=lat
             if lat<minlat:
                minlat=lat
             if lon>maxlon:
                maxlon=lon
             if lon<minlon:
                minlon=lon
            else:
             #self.warningsFile.write("<tr><td>intersect<td><a href='http://openstreetmap.org/browse/way/%s'>%s</a>" % (self.WayID,self.WayID))
             return 0
#           for i in self.waynodes:
#            if i in self.Nodes:
#             del self.Nodes[i] # let's not take borders in account # have to
           area = 0
           prx,pry= boundary[0]


           for x,y in boundary:
              area+=(x*pry-y*prx)/2
              prx = x
              pry = y
           area = abs(area)*9300 #FIXME: recount multiplier for Belarus
           IDsToCheck = []
           for i in range(int(minlat*self.ZoomLevel),int(maxlat*self.ZoomLevel)+1):
            if i in self.Tiles:
             for j in range(int(minlon*self.ZoomLevel),int(maxlon*self.ZoomLevel)+1):
              if j in self.Tiles[i]:
                IDsToCheck.extend(self.Tiles[i][j])
           self.Borders[id]={}
           nodesInWay = 0
	   labelID = 0

           nodesToChk = len(IDsToCheck)
           for id in IDsToCheck:
             if id in self.Nodes:
              nlat,nlon = self.Nodes[id]
              prx, pry = boundary[0]
              isin = False
              ynlon=0
              for x,y in boundary:

                if (nlat<x and nlat>prx) or (nlat>x and nlat<prx):
                 if y==pry:
                   ynlon=y
                 else:
                   ynlon=(y-pry)*(nlat-x)/(x-prx) + y
                 if (ynlon<nlon):
                  isin = not isin
                prx, pry = x, y
              if isin:
                nodesInWay += 1
#                delNode(self, id)
                if id in self.Places:
		  if (not self.tags.get('name')  or self.tags.get('name') == self.Places[id].get('name')):
                   labelID = id
                   #print id
                   for k,v in self.Places[id].items():
                     if k not in self.tags:
                      self.tags[k] = v
                   #del self.Places[id]
           place = {}
           if area<0.00000001:
             self.warningsFile.write("<tr><td>zero-area<td><a href=http://openstreetmap.org/browse/way/%s>%s</a>" % (self.WayID, self.WayID))
             return
	   if labelID == 0:
              self.BorderList.append((nodesInWay/area,area,nodesInWay, (minlat, minlon, maxlat, maxlon))) # a list of tuples that easily could be sorted by density
	   else:
             self.BPlaces[labelID] = (area, nodesInWay, (minlat, minlon, maxlat, maxlon),self.tags)
             #print self.BPlaces[labelID]
        else:					## TODO: relations
           self.warningsFile.write("<tr><td>non-circular<td><a href=http://openstreetmap.org/browse/way/%s>%s</a>"%\
              (id,id))
    elif name == 'node':
      #if(self.isInteresting):
       if 'place' in self.tags:
        self.Places[self.nodeID] = self.tags
        self.PlacesCount += 1
    elif name == 'relation':
      self.currentRelID = int(self.currentRelID)
      owntuple = ('relation',self.currentRelID)
      if self.tags.get('type', None) == 'address':
        def CreateAddrThg (rid):
         if rid not in self.Address:
          self.Address[rid] = {}
          self.Address[rid]["child"] = []
          self.Address[rid]["parent"] = ""
          self.Address[rid]["tags"] = {}
        CreateAddrThg(self.currentRelID)
        self.Address[self.currentRelID]["tags"] = self.tags
        for obj,role in self.currentMembers:
          mtype,mid = obj
          mid = int(mid)
          if role in ('a1', 'a2', 'a3','a4','a5', 'a6', 'house', 'label'):
            self.Address[self.currentRelID]["child"].append(obj)
            if mtype is 'relation':
              CreateAddrThg(mid)
              self.Address[mid]["parent"] = self.currentRelID
          elif role in ('is_in',):

            if mtype not in ('relation',):
              self.warningsFile.write("<tr><td>is_in not relation but %s<td>%s" % (mtype,linkRelation(self.currentRelID)))
            else:
              CreateAddrThg(mid)
              if owntuple not in self.Address[mid]["child"]:
                self.Address[mid]["child"].append(owntuple)
              self.Address[self.currentRelID]["parent"] = mid

if(__name__ == "__main__"):
  a = osmParser(sys.stdin)

