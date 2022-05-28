# chainget
Obtains the location/chainage of a point relative to a multi-line, and it's distance/offset from the multi-line.

Uses a Breath-First Search algorithm.

Required libraries: pandas, shapely

Known bugs:
If the point is outside the range of the multi-line (at the last or first point of the divided multi-line), the Breath-First search version of the code does not run, only the single iteration.
