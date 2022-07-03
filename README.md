# chainget
Obtains the location/chainage of a point relative to a multi-line, and it's distance/offset from the multi-line. Uses a Breath-First Search algorithm.


Required libraries: pandas, shapely, openpyxl


Inputs required:

A xlsx file of the points you wish to process (with x and y as headers)

A xlsx file of the multi-line you wish to process (with x and y as headers)


Known bugs:
If the point is outside the range of the multi-line (at or beyond the last or first point of the divided multi-line), the Breath-First Search version of the code does not run, only the single iteration version.
