#!/bin/sh
cd /var/www/latlon/stat/by/
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/belarus.osm.bz2|tee belarus.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py be Belarus routing > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..

cd kosovo
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/kosovo.osm.bz2|tee kosovo.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py sq Kosovo routing > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..


cd mk
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/macedonia.osm.bz2|tee macedonia.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py mk Macedonia routing > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..



cd lv
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/latvia.osm.bz2|tee latvia.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py en Latvia routing > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..

cd hr
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/croatia.osm.bz2|tee croatia.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py en Croatia routing > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..


cd tn
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://chdoula.lebonchoix.net/map.osm.bz2|tee tunisia.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py ru Tunisia routing > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..


cd ua 
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://download.geofabrik.de/osm/europe/ukraine.osm.bz2|tee ukraine.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py ru Ukraine routing > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..

cd ru
mkdir `date +0%Y.%m.%d`
cd `date +0%Y.%m.%d`
wget -q -O - http://osm.tesoro-shop.ru/russia.osm.bz2|tee russia.osm.bz2|bunzip2| /var/www/osm/stat/initialParse.py ru Russia norouting > bystats.html  2>bystats.err.html
cd ..
rm -f latest
ln -sf `date +0%Y.%m.%d`/ latest
cd ..
