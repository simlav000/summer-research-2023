import h5py
import numpy as np
import sys


"""
Author: Simon Lavoie
simon.lavoie@mail.mcgill.ca
Summer 2023

This script allows the user to quickly print the output from any simulation.
The code largely tells you how to use it. Just run the script from the command line and it
will ask you for a .h5 file to read. From there it will ask you which keys to extract
and print useful information about what is stored in said keys.
This script immediately uses the Flags and NumDetected arrays to infer the NumPhotons
and NumSources as specified by the YAML.
It also prints out the human-readable flag descriptions for each unique flag, alongside
how often each unique flag was seen (as a percentage).
"""

file_path = input("Enter path of file to visualize: ")
# Find the index where "chroma-simulation/" ends
index = file_path.rfind("chroma-simulation/") + len("chroma-simulation/")

# Get the parent directory
chroma_path = file_path[:index]
sys.path.append(chroma_path)
from Utilities import ProgressBar

with h5py.File(file_path, 'r') as hdf:
    keys = list(hdf.keys())

    MetaData = dict()
    for key, value in hdf.attrs.items():
        if isinstance(value, bytes):
            MetaData[key] = value.decode()
        else:
            MetaData[key] = value
    
    Generator = MetaData["Generator"]
    PhotonLocation = MetaData["PhotonLocation"]
    NumSources = int(MetaData["NumberOfSources"])
    NumSims = int(MetaData["NumberOfRuns"])

    # For most generation methods, NumPhotons is uniform. For 
    # generation methods like NEST, NumPhotons may be heterogeneous
    NumPhotons = np.array(hdf.get("NumPhotons").get("NumPhotons"))
    Sample = NumPhotons[0]
    # Same number of photons for each event
    if np.all(Sample == NumPhotons):
        NumPhotons = Sample
        TotalNumberOfPhotons = NumSources * NumPhotons * NumSims
        print(f"Number of photons: {NumPhotons}")
    else:
        TotalNumberOfPhotons = np.sum(NumPhotons)
        NumPhotons = np.mean(NumPhotons)
        print(f"Number of photons (on average): {NumPhotons}")

    print(f"Generator: {Generator}") 
    print(f"Number of sources: {NumSources}")
    print(f"Number of runs: {NumSims}")
    print(f"Total number of photons simulated: {TotalNumberOfPhotons}")
    print(f"PhotonLocation: {PhotonLocation}")

    flags_already_printed = False

    # Now we show the user which keys they may extract
    print(f"Keys which can be extracted:")
    for i, key in enumerate(keys):
        print(f"{i}: {key}\t")
    print("*: Extract All")

    # dictionary to store the extracted data
    extracted_data = {}

    # list of keys you want to extract data from
    keys_to_extract = []

    # This will break if/when there are more than 
    # 100 types of arrays being written as chroma outputs
    Integers = [str(i) for i in range(100)]
    while True:
        index_input = input("Enter index of keys you wish to extract (Press Enter when done): ")
        if index_input == "":
            break
        elif "*" in index_input:
            for key in keys:
                keys_to_extract.append(key)
            break
        elif index_input in Integers:
            keys_to_extract.append(keys[int(index_input)])
        else:
            print(f"Invalid input, try again")

    # Loop over the keys and extract the data
    for index, key in enumerate(keys_to_extract):
        ProgressBar(index, len(keys_to_extract), '  Extracting key %d of %d:' % (index + 1, len(keys_to_extract)))
        group = hdf.get(key)
        extracted_data[key] = np.array(group.get(key))

def interpretFlags():
    # At first glance, simply viewing the Flags array doesn't mean much to the user unless they are
    # very familiar with chroma so with this the user can translate the flags to their descriptions
    if "Flags" in keys_to_extract:
        Flags = extracted_data["Flags"]
        print_interactions_input = input("Do you wish to print all relevant flag descriptions? (y/n): ")

        if print_interactions_input.lower() in ["y", "yes"]:
            print("\n")
            flag_descriptions = {
                0: "NO_HIT",
                1: "BULK_ABSORB",
                2: "SURFACE_DETECT",
                3: "SURFACE_ABSORB",
                4: "RAYLEIGH_SCATTER",
                5: "REFLECT_DIFFUSE",
                6: "REFLECT_SPECULAR",
                7: "SURFACE_REEMIT",
                8: "SURFACE_TRANSMIT",
                9: "BULK_REEMIT",
                10: "MATERIAL_REFL",
                31: "NAN_ABORT"
            }

            def find_powers_of_2(n):
                powers = set()
                n_binary = bin(n)[2:]  # Convert to binary string and remove the "0b" prefix
                for index, char in enumerate(n_binary[::-1]):
                    if char == "1":
                        powers.add(index)
                return powers

            print("###Flags###")
            print(f"type: {type(Flags)}")
            print(f"shape: {Flags.shape}")

            unique_flags = {flag for flag in Flags}
            flag_count = {flag: 0 for flag in unique_flags}

            for flag in Flags:
                flag_count[flag] += 1

            for unique_flag, count in flag_count.items():
                output_string = ""
                keys = find_powers_of_2(unique_flag)
                for key in keys:
                    if output_string == "":
                        output_string += flag_descriptions[key]
                    else:
                        output_string += " + " + flag_descriptions[key]

                print(f"{unique_flag}: {output_string} (Percentage: {round(count / TotalNumberOfPhotons * 100,2)})")

            print("\n")
        elif print_interactions_input.lower() in ["n", "no"]:
            do_nothing = True                            
        else:
            print(f"Invalid input, try again.")
            interpretFlags()

interpretFlags()

def isInteger(str):
    if str == "":
        return False
    
    if isinstance(str, int):
        return True

    for i in range(len(str)):
        if str[i].isdigit() != True:
            return False

    return True

while True:
    print_arrays_input = input("Do you wish to print the arrays and their contents? (y/n): ")

    if print_arrays_input.lower() in ["y", "yes"]:
        print_arrays = True
        how_much_2_print = ""
        while not isInteger(how_much_2_print): 
            how_much_2_print = input("How many array entries do you wish to see? (Enter an integer or * to print all): ")
            if not isInteger(how_much_2_print):
                if "*" in how_much_2_print:
                    how_much_2_print = np.iinfo(np.int64).max
                else:
                    print("Please enter an integer.") 
        how_much_2_print = int(how_much_2_print)
        break
    elif print_arrays_input.lower() in ["n", "no"]:
        print_arrays = False
        break
    else: 
        print("Invalid input, try again.")

for key in keys_to_extract:
    print(f"###{str(key)}###")
    print(f"type: {type(extracted_data[key])}")
    print(f"shape: {extracted_data[key].shape}")
    if print_arrays:
        try:
            if how_much_2_print > len(extracted_data[key]):
                how_much_2_print = len(extracted_data[key])
            print(f"array: \n")
            print("[", end="")
            for i in range(how_much_2_print):
                if i < how_much_2_print - 1:
                    print(f"{extracted_data[key][i]}, ", end="")
                else:
                    print(f"{extracted_data[key][i]}", end="")
            print("]", end="")
            print("\n")
        except TypeError:
            print(f"{extracted_data[key]} is empty\n")
    else:
        print("\n")








