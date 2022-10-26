import numpy as np
from skimage import color

# peaked_color = '#262733'
# peaked_rgb = np.array((38,39,51))

colors_dict = {
"FFFFFF":"White", "F5F5DC":"Beige", "808080":"Grey", "000000":"Black",
"FF0000":"Red", "FF8000":"Orange", "FFFF00":"Yellow", "00CC00":"Green", 
"0000CC":"Blue", "6600CC":"Purple", "FF99FF":"Pink", "663300":"Brown"}

def findcolorname(peaked_color):
    # Get a list of color values in hex string format
    hex_rgb_colors = list(colors_dict.keys())

    r = [int(hex[0:2], 16) for hex in hex_rgb_colors]  # List of red elements.
    g = [int(hex[2:4], 16) for hex in hex_rgb_colors]  # List of green elements.
    b = [int(hex[4:6], 16) for hex in hex_rgb_colors]  # List of blue elements.

    r = np.asarray(r, np.uint8)  # Convert r from list to array (of uint8 elements)
    g = np.asarray(g, np.uint8)  # Convert g from list to array
    b = np.asarray(b, np.uint8)  # Convert b from list to array

    rgb = np.dstack((r, g, b)) #Stack r,g,b across third dimention - create to 3D array (of R,G,B elements).

    # Convert from sRGB color spave to LAB color space
    lab = color.rgb2lab(rgb)

    # Convert peaked color from sRGB color spave to LAB color space
    # hex2rgb
    peaked_rgb = np.asarray([int(peaked_color[1:3], 16), int(peaked_color[3:5], 16), int(peaked_color[5:7], 16)], np.uint8)
    peaked_rgb = np.dstack((peaked_rgb[0], peaked_rgb[1], peaked_rgb[2]))
    peaked_lab = color.rgb2lab(peaked_rgb)

    # Compute Euclidean distance from peaked_lab to each element of lab
    lab_dist = ((lab[:,:,0] - peaked_lab[:,:,0])**2 + (lab[:,:,1] - peaked_lab[:,:,1])**2 + (lab[:,:,2] - peaked_lab[:,:,2])**2)**0.5

    # Get the index of the minimum distance
    min_index = lab_dist.argmin()

    # Get hex string of the color with the minimum Euclidean distance (minimum distance in LAB color space)
    peaked_closest_hex = hex_rgb_colors[min_index]

    # Get color name from the dictionary
    color_name = colors_dict[peaked_closest_hex]
    color_name = color_name.lower()
    if 'black' in color_name:
        color_name = 'Black'
    elif 'white' in color_name:
        color_name = 'White'
    elif 'beige' in color_name:
        color_name = 'Beige'
    elif any(x in color_name for x in ['gray','grey']):
        color_name = 'Grey'
    elif 'red' in color_name:
        color_name = 'Red'
    elif 'orange' in color_name:
        color_name = 'Orange'
    elif 'yellow' in color_name:
        color_name = 'Yellow'
    elif 'green' in color_name:
        color_name = 'Green'
    elif 'blue' in color_name:
        color_name = 'Blue'
    elif any(x in color_name for x in ['purple','violet']):
        color_name = 'Purple'
    elif any(x in color_name for x in ['brown', 'coffee']):
        color_name = 'Brown'
    elif 'pink' in color_name:
        color_name = 'Pink'
    else:
        color_name = 'Other'
    return color_name

# print("Peaked color name: " + color_name)
