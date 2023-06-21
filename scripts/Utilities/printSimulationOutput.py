import h5py
import numpy as np

"""
This script is just used to be able to quickly visualize the output from any simulation.
The code largely tells you how to use it. Just run the script from the command line and it
will ask you for a .h5 file to read. From there it will ask you which keys to extract
and print useful information about what is stored in said keys.
"""

file_path = input("Enter path of file to visualize: ")

with h5py.File(file_path, 'r') as hdf:
    keys = list(hdf.keys())

    # First we can infer how many photons and sources were input in the yaml
    # for this simulation using NumDetected and Flags. These are the least memory
    # intensive keys to extract as they contain arrays of integers as opposed to 
    # multidimentional arrays
    NumDetectedGroup = hdf.get("NumDetected")
    FlagsGroup = hdf.get("Flags")
    NumDetected = np.array(NumDetectedGroup.get("NumDetected"))
    Flags = np.array(FlagsGroup.get("Flags"))
    NumberOfSources = len(NumDetected)
    TotalNumberOfPhotons = len(Flags)
    NumberOfPhotons = int(TotalNumberOfPhotons / NumberOfSources)

    print(f"Simulation input parameters: ")
    print(f"NumberOfPhotons: {NumberOfPhotons}")
    print(f"NumberOfSources: {NumberOfSources}")
    print(f"TotalNumberOfPhotons: {TotalNumberOfPhotons}\n")

    # Now we show the user which keys they may extract
    print(f"Keys which can be extracted:")
    for i, key in enumerate(keys):
        print(f"{i}: {key}\t")
    print("*: Extract All")

    # dictionary to store the extracted data
    extracted_data = {}

    # list of keys you want to extract data from
    keys_to_extract = []

    while True:
        index_input = input("Enter index of keys you wish to extract (Press Enter when done): ")
        if index_input == "":
            break
        elif "*" in index_input:
            for key in keys:
                keys_to_extract.append(key)
            break
        else:
            keys_to_extract.append(keys[int(index_input)])

    # Loop over the keys and extract the data
    for key in keys_to_extract:
        group = hdf.get(key)
        extracted_data[key] = np.array(group.get(key))

    print_arrays_input = input("Do you wish to print the arrays and their contents (y/n)?: ")
    
    if print_arrays_input.lower() in ["y", "yes"]:
        print_arrays = True
    else:
        print_arrays = False

    for key in keys_to_extract:
        print(f"###{str(key)}###\n")
        print(f"type: {type(extracted_data[key])}")
        print(f"shape: {extracted_data[key].shape}")
        if print_arrays:
            print(f"value: {extracted_data[key]}\n")
        else:
            print("\n")








