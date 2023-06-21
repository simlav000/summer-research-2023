import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import sys


# This script plots the detected photons onto a projection of the surface of the detector (which is a cylinder) which is shown as a 2D rectangle
# The photons are plotted as a heatmap, where brighter colours represent a larger number of photon counts. Use less bins for less photons.

# Intended use case: python3 plotDetectedPhotons.py <PATH> <BIN_COUNT>
# where <PATH> is the path to a HDF5 file to process.
# and <BIN_SIZE> defines the resolution of the image. Use larger numbers for large simulations.
# 100,000 is about the upper limit for before memory issues become a problem

# This script assumes you have the ability to view the generated plot. From this window,
# the user may decide where to save it, if saving it is desired

def plotDetectedPhotons(file_path, bin_count):
    with h5py.File(file_path, 'r') as hdf:
        # dictionary to store the extracted data
        extracted_data = {}

        # list of desired keys to extract data from
        keys_to_extract = ['DetectedPos', 'DetectorHit']

        # Loop over the keys and extract the data
        for key in keys_to_extract:
            group = hdf.get(key)
            extracted_data[key] = np.array(group.get(key))

        # Access the extracted data
        DetectedPos = extracted_data['DetectedPos']

    x, y, z = np.transpose(DetectedPos)

    # Not general, only true for nEXO
    r = 760 # mm

    # Map from (x, y) points into angle from positive x-axis
    theta = np.mod(np.arctan2(y, x), 2 * np.pi)
    projection = r * theta

    # Create a 2D histogram
    heatmap, xedges, yedges = np.histogram2d(projection, z, bins=bin_count)

    # Define the colormap
    cmap = colors.LinearSegmentedColormap.from_list('my_colormap', ['black', '#972AA8', 'white'])

    # Plot the heatmap
    plt.imshow(heatmap.T, origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap=cmap)
    plt.colorbar(label='Photon Count')

    # Set labels and title
    plt.xlabel('$r\\theta$ (mm)')
    plt.ylabel('Z-coordinate')
    plt.title('Detector Position on Cylindrical Projection')

    # Display the plot
    plt.show()

def read_file(file_path):
    try:
        plotDetectedPhotons(file_path, bin_count)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"Error reading file '{file_path}'.")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Please provide a file path and bin size as an argument.")
    else:
        file_path = sys.argv[1]
        bin_count = int(sys.argv[2])
        read_file(file_path)

