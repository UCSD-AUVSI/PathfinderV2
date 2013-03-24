Pathfinder generates a path that the UAV will traverse. The follow input arguments are 
necessary for the algorithm to function:

  1. The boundaries of the search area
  2. The initial location of the plane
  3. The direction of the wind
  4. `overshoot_distance`: The distance it takes the plane to level itself after turning
  5. `path_width`: The horizontal distance of the field that the camera can capture in one shot

As output, the algorithm returns a list of coordinates that the plane can traverse to 
capture the entire search area. Note that the algorithm assumes a 2D euclidian coordinate
system. In practice, using GPS coordinates is fine.

Algorithm
---------

  1. Parallel lines are drawn over the search area in the direction of the wind. Each line is
     `path_width` units apart.
  2. The lines are broken up into line segments, and the line segments are cropped
     at the borders of the search area.
  3. `overshoot_distance` units are added to the top and bottom of each line segment
  4. Starting from the plane location, a path is generated using the following algorithm:
    a. From the current point, find the nearest point in any line segment that hasn't been 
       seen
    b. Add that point to the path, followed by the other point in that line segment
    c. Mark that line segment as seen, and set the current point to the end of the line segments
    d. Repeat until all line segments have been seen

Algorithm Rationale
-------------------

  This algorithm was chosen to address a couple concerns:
  
  1. The resulting path primarily has the plane flying into or against the wind, 
     therefore reducing the distance that the plane will veer off track
  2. By padding each line segment by the distance it takes to level the plane, it ensures
     that the plane will always be flying level when it is over the search area
 
Requirements
------------

  Pathfinder requires that the following libraries be installed:
    - numpy (pip install numpy)
    - scipy (pip install scipy)
    - shapely 
      * GEOS must be installed first. on mac os x you can use `brew install geos`
      - Can be installed with `pip install shapely`
    - Python Imaging Libary (recommended)
      - Can be installed with `pip install pil`
      - PIL is only used to render the images for the map, so it is not technically
        necessary, but useful

How to Run
----------

  1. Modify `main` in pathfinder.py with the coordinates that you wish to use
  2. Open a console and run: `python pathfinder.py`
  3. The path will be output to `STDOUT` in QGC format, and the image of the path and search
     area will be saved to `output.jpg`
