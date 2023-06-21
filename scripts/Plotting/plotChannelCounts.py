import numpy as np
import h5py
import pandas as pd
import matplotlib.pyplot as plt
import sys

def plotChannelCounts(file_path):
    with h5py.File(file_path, 'r') as hdf:
        # dictionary to store the extracted data
        extracted_data = {}

        # list of keys you want to extract data from
        keys_to_extract = ['ChannelCharges', 'ChannelIDs']

        # Loop over the keys and extract the data
        for key in keys_to_extract:
            group = hdf.get(key)
            extracted_data[key] = np.array(group.get(key))

        # Access the extracted data
        ChannelCharges = extracted_data['ChannelCharges']
        ChannelIDs = extracted_data['ChannelIDs']

    SortedChannelCharges = np.zeros(720)
    for i in range(len(ChannelIDs)):
        SortedChannelCharges[ChannelIDs[i]] += ChannelCharges[i]

    SortedChannelIDs = np.arange(720)

    plt.bar(SortedChannelIDs, SortedChannelCharges, color="black")
    plt.title("Bar Chart of Photon Count Over Channel IDs")
    plt.xlabel("Channel ID")
    plt.ylabel("Photon Count")
    plt.show()

def read_file(file_path):
    try:
        plotChannelCounts(file_path)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"Error reading file '{file_path}'.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a file path and bin size as an argument.")
    else:
        file_path = sys.argv[1]
        read_file(file_path)


