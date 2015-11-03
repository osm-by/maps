# Конвертация карт [OpenStreetMap](http:\\osm.org) в форматы Garmin и Navitel с использованием osm2mp

## установка необходимых программ
  1. Скачать и установить ActivePerl — http://www.activestate.com/activeperl/
  1. Выполнить Dos-команду \Perl\bin\ppm.bat.
В окрывшемся, через некоторое время, окне Perl Package Manager (PPM) выбрать в меню View команду All Packages
    * найти в списке модуль Template-toolkit и выделить его
    * В меню Action (или в контекстном меню по правому клику) выполнить команду Install Template-toolkit
    * Таким же образом отметить для установки модули (если они еще не установлены):
      1. Getopt-Long
      1. Text-Unidecode
      1. List-MoreUtils
      1. Math-Polygon
      1. Math-Polygon-Tree
      1. Math-Geometry-Planar-GPC-Polygon
      1. YAML
      1. Tree-R
  1. В меню File выполнить команду Run Marked Actions
  1. Выйти из PPM
  1. скачиваем послед версию osm2mp http://osm2mp.googlecode.com/svn/trunk/osm2mp/ - все файлы в отдельную папку (C:\Perl\site\osm2mpnew)

## конвертация для Navitel

### скачиваем файлы конфигурации

скачиваем в папку с osm2mp (C:\Perl\site\osm2mpnew) [белорусские](http://maps-by.googlecode.com/files/osm2mp_conf_by.rar) или [российские](http://osm2navitel.googlecode.com/svn/trunk/) конфиги

отличия
  1. футвеи у второго не роутинговые и проподают на маштабах отличных от 120м, у первого футвеи тоже нероутинговые но заменен другим типом, который не проподает
  1. заборы во втором не конвертируются в городах, в первом-конвертятся - если мешает - используем [скин](http://forum.openstreetmap.org/viewtopic.php?pid=59999#p59999), где забор -отличается по цвету от дорог
  1. отличия в приоритетах дорог
  1. отличия в определений грунтовых/негрунтовых дорогах

### устанавливаем GPSMAPEDIT

http://www.geopainting.com/ru/

## непосредственно конвертация

  1. скачиваем [обработанный дамп карты РБ](ftp://188.40.19.246/osm/dumps/belarus.current.preprocessed.osm.bz2) [OSM](http://osm.org) от [GeoFabric](http://download.geofabrik.de/osm/europe/) (обновляется ежедневно) или другой необходимый [дамп](http://download.geofabrik.de/osm/)
  1. пуск-выполнить cmd
  1. ввести cd C:\Perl\site\osm2mpnew
  1. ввести osm2mp.pl --osmbbox --navitel --addrinterpolation --disableuturns --config=navitel.yml belarus.current.preprocessed.osm > belarus.mp
  1. после конвертации появится файл belarus.mp, открываем его МапЕдитом и делаем "tools->split map to files" по сетке 9x20, появится 2 мп файла(если это РБ)
  1. каждый mp файл открываем gpsmapedit-ом и исправляем ошибки
    * (tools->veryfy map->(отмеченным оставить только "find misaligned/duplicated..."))
    * для каждой найденной ошибки - нажимаем на нее 2 раза при этом выделяется точка в центре в панеле сверху выбираем кнопку "Edit nodes" правой кнопкой на ней и "connect to nearest nodes"
  1. после исправление всех ошибок, проверяем "verify map"
  1. делаем их экспорт в навител
  1. кладем к этим двум файлам карту мира и закачиваем эти 3 файла в отдельный атлас.
