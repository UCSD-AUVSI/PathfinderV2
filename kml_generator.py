class KMLGenerator:
    """
	Outputs the path waypoints to a format that can be displayed by
	Google Earth.
    """

    def __init__(self, pathfinder):
	self.pathfinder = pathfinder

    def export_kml(self):
	def print_header():
	    print '<?xml version="1.0" encoding="UTF-8"?>'
	    print '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">'
	    print '<Folder>'
		
	def print_boundaries():
	    print '<Style id="boundarystyle">'
	    print '\t<PolyStyle>'
	    print '\t\t<color>8000ff00</color>'
	    print '\t</PolyStyle>'
	    print '\t</Style>'
	    print '<Placemark>'
	    print '\t<name>Flight Boundaries</name>'
	    print '\t<styleUrl>#boundarystyle</styleUrl>'
	    print '\t<Polygon>'
	    print '\t\t<extrude>1</extrude>'
	    print '\t\t<altitudeMode>clampToGround</altitudeMode>'
	    print '\t\t<outerBoundaryIs>'
	    print '\t\t\t<LinearRing>'
	    print '\t\t\t\t<coordinates>'
	    for index, (x,y) in enumerate(self.pathfinder.get_boundaries()):
		lat = "%.6f"%x
		lng = "%.6f"%y

		print '\t\t\t\t\t%s,%s,%s'%(lng, lat, "0.0")

	    print '\t\t\t\t</coordinates>'
	    print '\t\t\t</LinearRing>'
	    print '\t\t</outerBoundaryIs>'
	    print '\t</Polygon>'
	    print '</Placemark>'

	def print_searcharea():
	    print '<Style id="searchareastyle">'
	    print '\t<PolyStyle>'
	    print '\t\t<color>ccff0000</color>'
	    print '\t</PolyStyle>'
	    print '\t</Style>'
	    print '<Placemark>'
	    print '\t<name>Search Area</name>'
	    print '\t<styleUrl>#searchareastyle</styleUrl>'
	    print '\t<Polygon>'
	    print '\t\t<color>ccff0000</color>'
	    print '\t\t<extrude>1</extrude>'
	    print '\t\t<altitudeMode>clampToGround</altitudeMode>'
	    print '\t\t<outerBoundaryIs>'
	    print '\t\t\t<LinearRing>'
	    print '\t\t\t\t<coordinates>'
	    for index, (x,y) in enumerate(self.pathfinder.get_searcharea()):
		lat = "%.6f"%x
		lng = "%.6f"%y

		print '\t\t\t\t\t%s,%s,%s'%(lng, lat, "0.0")

	    print '\t\t\t\t</coordinates>'
	    print '\t\t\t</LinearRing>'
	    print '\t\t</outerBoundaryIs>'
	    print '\t</Polygon>'
	    print '</Placemark>'

	def print_path():
	    print '<Placemark>'
	    print '\t<name>Flight Path</name>'
	    print '\t<LineString>'
	    print '\t<extrude>1</extrude>'
	    print '\t<tesselate>1</tesselate>'
	    print '\t<coordinates>'
	    for index, (x, y) in enumerate(self.pathfinder.get_path()):
		lat = "%.6f"%x
		lng = "%.6f"%y
		alt = str(self.pathfinder.get_altitude())

		print '\t\t%s,%s,%s'%(lng, lat, alt)

	    print '\t</coordinates>'
	    print '\t</LineString>'
	    print '</Placemark>'

	def print_points():
	    for index, (x, y) in enumerate(self.pathfinder.get_path()):
		lat = "%.6f"%x
		lng = "%.6f"%y
		alt = str(self.pathfinder.get_altitude())

		print '<Placemark>'
		print '\t<name>WP %i</name>'%index
		print '\t<Point>'
		print '\t\t<coordinates>%s,%s,%s</coordinates>'%(lng, lat, alt)
		print '\t</Point>'
		print '\t</Placemark>'

	def print_footer():
	    print '</Folder>'
	    print '</kml>'

	print_header()
	print_searcharea()
	print_boundaries()
	print_path()
	print_points()
	print_footer()
