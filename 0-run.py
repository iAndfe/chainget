## Note read this:
# Install python on to your computer
# https://www.python.org/downloads/

# Install libraries using command:
# pip install pandas shapely openpyxl

import pandas as pd

# Import functions from chaintools.py
from chaintools import dividechain
from chaintools import chainget
from chaintools import plot_points

# User input
filename_road = str(input('Enter road name: '))
filename_points = str(input('Enter points name: '))
precision = float(input('Enter precision in m (eg. 0.1): '))

# Read from excel files
road = pd.read_excel(filename_road + '.xlsx')
points = pd.read_excel(filename_points + '.xlsx')

# Export output to "points_processed.xlsx"
chain = dividechain(road, precision)
points_processed = chainget(chain, points)
points_processed.to_excel(filename_points + '_' + filename_road + '_processed.xlsx')

# Plot road and points, and save to "plot.pdf"
plot_points(points, road, limit = 50)