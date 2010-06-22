#!/usr/bin/ruby

class OziGCP
	attr_reader :x, :y
	def initialize(line)
		if not line =~ /Point[0-9]{2},xy, +[0-9]+, +[0-9]+,in, deg, +[0-9]+,.*, grid,   ,           ,           ,N/
			raise "No point definition"
		end

		fields = line.split(',')
		@x = fields[2].to_i
		@y = fields[3].to_i
		@lat_deg = fields[6].to_i
		@lat_min = fields[7].to_f
		@lat_side = fields[8]
		@lon_deg = fields[9].to_i
		@lon_min = fields[10].to_f
		@lon_side = fields[11]
	end

	def geo_to_s
		sprintf("%dd%f%s %dd%f%s", @lon_deg, @lon_min, @lon_side, @lat_deg, @lat_min, @lat_side)
	end

	def lat
		sprintf("%dd%f%s", @lat_deg, @lat_min, @lat_side)
	end

	def lon
		sprintf("%dd%f%s", @lon_deg, @lon_min, @lon_side)
	end
end


class OziMap
	attr_reader :gcps
	def initialize(file, geo_cs, projection)
		if file.kind_of?(String)
			lines = IO.read(file).split(/\r?\n/)
		else
			if file.kind_of?(IO)
				lines = file.read.split(/\r?\n/)
			else
				raise "Unknown datasource"
			end
		end

		@gcps = []

		lines[9..38].each { |line|
			begin
				gcp = OziGCP.new(line)
				gcps << gcp
			rescue
			end
		}
		@geo_cs = geo_cs
		@projection = projection
	end

	def gcp_clip_rect
		minx = maxx = @gcps[0].x
		miny = maxy = @gcps[0].y

		@gcps.each {|p|
			minx = p.x if minx > p.x
			miny = p.y if miny > p.y
			maxx = p.x if maxx < p.x
			maxy = p.y if maxy < p.y
		}
		{:x1 => minx, :y1 => miny, :x2 => maxx, :y2 => maxy, :w => maxx - minx + 1, :h => maxy - miny + 1}
	end
end


def run_cmd(cmd, *args)
	STDERR.puts cmd + " " + args.join(" ")
	system(cmd + " " + args.join(" "))
end

require 'open3'
class PROJ4Utils
	def self.cs2cs(s_srs, t_srs, points)
		out = ''
		STDERR.puts "cs2cs #{s_srs} +to #{t_srs}"
		Open3.popen3("cs2cs #{s_srs} +to #{t_srs}") { |stdin, stdout, stderr|
			points.each {|p| stdin.puts p}
			stdin.close
			out = stdout.read
		}
		STDERR.puts out

		t_points = []
		out.split(/\r?\n/).each {|line|
			x, y, hz = line.split
			t_points << {:x => x, :y => y}
		}
		t_points
	end
end

require 'optparse'
require 'ostruct'
require 'pp'

options = OpenStruct.new
#options.s_srs = "+proj=latlong +ellps=krass +towgs84=23.92,-141.27,-80.9,0,-0.37,-0.82,-0.12 +no_defs"
#options.t_srs = "+proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=5500000 +y_0=0 +ellps=krass +towgs84=23.92,-141.27,-80.9,0,-0.37,-0.82,-0.12 +no_defs"
options.s_srs = "+init=epsg:4179"
options.t_srs = "+init=epsg:3335 +lon_0=27 +x_0=5500000"

OptionParser.new do |opts|
	opts.banner = "Usage: #{$0} -s_srs <proj> -t_srs <proj> -m <file.map> -i <input image> -o <output GeoTIFF>"

	opts.on("-s SRS", "Source geospatial reference system") {|srs| options.s_srs = srs}
	opts.on("-t SRS", "Target geospatial reference system") {|srs| options.t_srs = srs}
	opts.on("-m MAP", "Ozi map file") {|map| options.mapfile = map}
	opts.on("-i INPUT", "Input Image") {|img| options.infile = img}
	opts.on("-o OUTPUT", "Output Image") {|img| options.outfile = img}
end.parse!

p options

s_proj = options.s_srs
t_proj = options.t_srs

tmp1 = `mktemp -u -t ozi2tiff.1.XXXXXX`.chomp + ".tif"
tmp2 = `mktemp -u -t ozi2tiff.2.XXXXXX`.chomp + ".tif"
tmp3 = `mktemp -u -t ozi2tiff.3.XXXXXX`.chomp + ".tif"

begin
	map = OziMap.new(options.mapfile, s_proj, t_proj)
	gcps_geo = []
	map.gcps.each {|p| gcps_geo << p.geo_to_s}
	t_gcps = PROJ4Utils.cs2cs(s_proj, t_proj, gcps_geo)

	clip_rect = map.gcp_clip_rect
	STDERR.puts "Map window:" + clip_rect.inspect

	args = "-srcwin #{clip_rect[:x1]} #{clip_rect[:y1]} #{clip_rect[:w]} #{clip_rect[:h]}"
	t_gcps.each_index {|i| args += " -gcp #{map.gcps[i].x - clip_rect[:x1]} #{map.gcps[i].y - clip_rect[:y1]} #{t_gcps[i][:x]} #{t_gcps[i][:y]}"}

	run_cmd("gdal_translate", "-a_srs", "'#{t_proj}'", "-expand rgb", args, options.infile, tmp1)
	run_cmd("gdalwarp", "-tps -dstnodata '0 255 0 0' -r cubic -multi", tmp1, tmp2)
#	run_cmd("convert", "-depth 8 -type Palette -compress None -transparent-color #00ff00", tmp2, tmp3)
	run_cmd(File.dirname($0) + "/rgb2pct.py","-s", options.infile, tmp2, tmp3)
	run_cmd("gdal_translate", '-co', 'tiled=yes', '-co', 'blockxsize=256', '-co', 'blockysize=256', '-co', 'compress=deflate', '-co', 'predictor=1', '-co', 'zlevel=9', tmp3, options.outfile)
ensure
	begin
		File.unlink(tmp1, tmp2, tmp3)
	rescue
	end
end

