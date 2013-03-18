class WaypointGenerator:
    def __init__(self, pathfinder):
        self.pathfinder = pathfinder

    def export_qgc_waypoints(self):
        def print_header():
            print "QGC WPL 110"
        def print_home_location():
            home_lat, home_lon = self.pathfinder.plane_location
            print "0\t1\t0\t16\t0\t0\t0\t0\t" + str(home_lat) + "\t" + \
                    str(home_lon) + "\t300.000000\t1"
        def print_path():
            for index, (x, y) in enumerate(self.pathfinder.get_path()):
                xstr = "%.6f" % x
                ystr = "%.6f" % y
                print str(index+1)\
                    +"\t0\t3\t16\t0.000000\t0.000000\t0.000000\t0.000000\t"+\
                    xstr+ "\t" + ystr + "\t300.000000\t1" 
        
        print_header()
        print_home_location()
        print_path()
