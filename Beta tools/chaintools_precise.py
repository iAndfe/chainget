# More precision
# chaintools suite

# Function: dividechain
def dividechain(road, precision):
    from shapely.geometry import LineString, MultiPoint, MultiLineString
    from shapely.ops import split
    import pandas as pd
    import numpy as np

    road_x = road["x"]
    road_y = road["y"]

    num_lines = len(road_x)-1
    lines = [0]*num_lines

    for i in range(num_lines):
        lines[i] = LineString([(road_x[i], road_y[i]), (road_x[i+1], road_y[i+1])])

    road_line = MultiLineString(lines)
    road_length = road_line.length

    di = round(road_length*1000000000)

    # Set precision (in nanometers, lower is more accurate)
    interval = 1000000000*precision

    chainage_points = MultiPoint([road_line.interpolate(((i*interval)/di), normalized=True) for i in range(0, int(di/interval))])
    chainage_points_x = [p.x for p in chainage_points.geoms]
    chainage_points_y = [p.y for p in chainage_points.geoms]
    chainage_points_chain_array = np.arange(start=0, stop=len(chainage_points_x)*precision, step=precision)
    chainage_points_chain = chainage_points_chain_array.tolist()

    df = pd.DataFrame(chainage_points_x, columns = ['x'])
    df['y'] = chainage_points_y
    df['chain'] = chainage_points_chain

    return df

# Function: chainget
def chainget(chainage, points):
    # Note, inputs must be csv files
    # input and chainage files, must have 'x' and 'y' columns.
    # chainage file must have 'chain' column

    import pandas as pd
    import numpy as np

    chainage_x = chainage["x"]
    chainage_y = chainage["y"]
    chainage_chain = chainage["chain"]
    points_x = points["x"]
    points_y = points["y"]

    num_points = len(points_x)
    num_chainage = len(chainage_x)

    # Obtain arrays from lists
    chainage_x_array = np.tile(chainage_x, (num_points, 1))
    chainage_y_array = np.tile(chainage_y, (num_points, 1))

    points_x_array = np.tile(points_x, (num_chainage, 1))
    points_y_array = np.tile(points_y, (num_chainage, 1))

    points_x_array = np.transpose(points_x_array)
    points_y_array = np.transpose(points_y_array)

    # Calculate distance/difference between points
    difference = np.sqrt(np.square(chainage_x_array - points_x_array) + np.square(chainage_y_array - points_y_array))
    difference2 = np.transpose(difference)

    # Export data to lists and csv
    points_chainage = [0]*num_points
    points_offset = [0]*num_points

    points_offset = np.amin(difference2, axis = 0)
    points_offset = np.ndarray.tolist(points_offset)

    points_chainage_locations = np.where(difference2 == np.amin(difference2, axis = 0))
    points_chainage_locations_values = points_chainage_locations[0]
    points_chainage_locations_index = points_chainage_locations[1]

    for i in range(num_points):
        points_chainage[points_chainage_locations_index[i]] = chainage_chain[points_chainage_locations_values[i]]

    points['Chainage'] = points_chainage
    points['Offset'] = points_offset

    return points

## Plot points and road function
def plot_points(points, road, limit):

    # Import matplotlib and pandas library
    import pandas as pd
    from matplotlib import pyplot as plt

    # Load road and points from .csv
    road_x = road["x"]
    road_y = road["y"]
    points_x = points["x"]
    points_y = points["y"]

    # Set limit of plot boundaries from min/max co-ords
    min_x = min(min(points_x), min(road_x)) - limit
    min_y = min(min(points_y), min(road_y)) - limit

    max_x = max(max(points_x), max(road_x)) + limit
    max_y = max(max(points_y), max(road_y)) + limit

    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)

    # Add points and road to plot
    plt.plot(road_x, road_y)
    plt.plot(points_x, points_y, 'ko', markersize = 1)

    plt.gca().set_aspect('equal', adjustable='box')

    # Print plot to pdf
    plt.savefig('plot.pdf')

    return print('...Saved to pdf')

def chainget_again(chainage, points, old_precision, new_precision):    
    import pandas as pd
    import numpy as np
    
    num_points = len(points)
    chainage_new = num_points*[0]
    offset_new = num_points*[0]
    nano_chains = num_points*[0]
    point_processed_array = num_points*[0]
    point_on_nano_chain = [0]*num_points

    for i in range(0, num_points):
        index_point = int(points.iloc[i]['Chainage']/old_precision)
        microLines_1_x = chainage.iloc[index_point]['x']
        microLines_1_y = chainage.iloc[index_point]['y']
        microLines_1_chain = chainage.iloc[index_point]['chain']

        microLines_2_x = chainage.iloc[index_point+1]['x']
        microLines_2_y = chainage.iloc[index_point+1]['y']
        microLines_2_chain = chainage.iloc[index_point+1]['chain']
        
        microLines_0_x = chainage.iloc[index_point-1]['x']
        microLines_0_y = chainage.iloc[index_point-1]['y']
        microLines_0_chain = chainage.iloc[index_point-1]['chain']

        point_microline_x = [microLines_0_x, microLines_1_x, microLines_2_x]
        point_microline_y = [microLines_0_y, microLines_1_y, microLines_2_y]
        point_microline_chain = [microLines_0_chain, microLines_1_chain, microLines_2_chain]
        
        micro_chain = pd.DataFrame(point_microline_x, columns = ['x'])
        micro_chain['y'] = point_microline_y
        micro_chain['chain'] = point_microline_chain

        nano_chain = dividechain(micro_chain, new_precision)
        nano_chains[i] = pd.DataFrame.to_numpy(nano_chain)
        point = pd.DataFrame([[points['x'][i], points['y'][i]]], columns=list('xy'))

        point_processed = chainget(nano_chain, point)
        point_processed_array[i] = pd.DataFrame.to_numpy(point_processed)
        point_on_nano_chain[i] = point_processed_array[i][0][2]    
        chainage_new[i] = microLines_0_chain + float((point_processed['Chainage']))
        offset_new[i] = float(point_processed['Offset'])

    points['Chainage'] = chainage_new
    points['Offset'] = offset_new

    return points, nano_chains, point_on_nano_chain

def chainget_again2(points, old_precision, new_precision, nano_chains, point_on_nano_chain):
    import pandas as pd
    import numpy as np

    num_points = len(points)
    chainage_new = num_points*[0]
    offset_new = num_points*[0]
    pico_chains = num_points*[0]
    point_processed_pico_array = num_points*[0]
    point_on_pico_chain = [0]*num_points
    orginal_chainage = points['Chainage'].tolist()

    for i in range(0, num_points):
        chainage_neo = pd.DataFrame(nano_chains[i], columns = ['x','y','chain'])
        index_point = int(point_on_nano_chain[i]/old_precision)
        microLines_1_x = chainage_neo.iloc[index_point]['x']
        microLines_1_y = chainage_neo.iloc[index_point]['y']
        microLines_1_chain = chainage_neo.iloc[index_point]['chain']

        microLines_2_x = chainage_neo.iloc[index_point+1]['x']
        microLines_2_y = chainage_neo.iloc[index_point+1]['y']
        microLines_2_chain = chainage_neo.iloc[index_point+1]['chain']
        
        microLines_0_x = chainage_neo.iloc[index_point-1]['x']
        microLines_0_y = chainage_neo.iloc[index_point-1]['y']
        microLines_0_chain = chainage_neo.iloc[index_point-1]['chain']

        point_microline_x = [microLines_0_x, microLines_1_x, microLines_2_x]
        point_microline_y = [microLines_0_y, microLines_1_y, microLines_2_y]
        point_microline_chain = [microLines_0_chain, microLines_1_chain, microLines_2_chain]
        
        micro_chain = pd.DataFrame(point_microline_x, columns = ['x'])
        micro_chain['y'] = point_microline_y
        micro_chain['chain'] = point_microline_chain

        pico_chain = dividechain(micro_chain, new_precision)
        pico_chains[i] = pd.DataFrame.to_numpy(pico_chain)
        
        point = pd.DataFrame([[points['x'][i], points['y'][i]]], columns=list('xy'))

        point_processed = chainget(pico_chain, point)
        point_processed_pico_array[i] = pd.DataFrame.to_numpy(point_processed)
        point_on_pico_chain[i] = point_processed_pico_array[i][0][2]
        chainage_new[i] = float((point_processed['Chainage'])) + orginal_chainage[i] - old_precision
        offset_new[i] = float(point_processed['Offset'])

    points['Chainage'] = chainage_new
    points['Offset'] = offset_new

    return points, pico_chains, point_on_pico_chain

def meta_chainget(road, points, precision):
    import pandas as pd
    from chaintools import dividechain
    from chaintools import chainget
    from chaintools import chainget_again
    from chaintools import chainget_again2

    # First Iteration
    iterations = precision
    chain = [0]*(iterations)
    point_on_chain = [0]*(iterations)

    precisions = [0.0]*(iterations+2)
    precisions[0] = 1

    for i in range(1, iterations+2):
        precisions[i] = precisions[i-1]/10

    chainage = dividechain(road, precisions[0])

    #2nd iteration
    points = chainget(chainage, points)
    points, chain[0], point_on_chain[0] = chainget_again(chainage, points, precisions[0], precisions[1])

    # Third+ Iteration
    for i in range(iterations-1):
        points, chain[i+1], point_on_chain[i+1] = chainget_again2(points, precisions[i+1], precisions[i+2], chain[i], point_on_chain[i])
    
    return points