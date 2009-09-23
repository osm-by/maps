#!/bin/sh
mount /var/www
cd /var/www/osm/stat/
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/belarus.osm.bz2|tee belarus.osm.bz2|bunzip2| ../initialParse.py Belarus > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest

cd kosovo
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/kosovo.osm.bz2|tee kosovo.osm.bz2|bunzip2| ../../initialParse.py Kosovo > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..


cd mk
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/macedonia.osm.bz2|tee macedonia.osm.bz2|bunzip2| ../../initialParse.py Macedonia > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..



cd lv
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/latvia.osm.bz2|tee latvia.osm.bz2|bunzip2| ../../initialParse.py Latvia > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..

cd hr
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/croatia.osm.bz2|tee croatia.osm.bz2|bunzip2| ../../initialParse.py Croatia > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..


cd tn
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://chdoula.lebonchoix.net/map.osm.bz2|tee tunisia.osm.bz2|bunzip2| ../../initialParse.py Tunisia > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..


cd ua 
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/ukraine.osm.bz2|tee ukraine.osm.bz2|bunzip2| ../../initialParse.py Ukraine > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..

cd ru
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://osm.tesoro-shop.ru/russia.osm.bz2|tee russia.osm.bz2|bunzip2| ../../initialParse.py Russia > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..


