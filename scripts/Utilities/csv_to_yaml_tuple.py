import csv
import os
import yaml
import pandas as pd

"""
This script is designed specifically to read wavelength and index of refraction data from a CSV file
and format it into yaml for use in chroma.

Usage: Run the script from the command line. The script will prompt the user to input a directory holding
CSV files. It will then prompt the user to input a filename for which the script will write to. The CSV
files should contain a header, and have two or three columns:
wavelength (wl), refraction coefficient (n), and extinction coefficient (k). 

The output of the script looks something like:

Material1:
  IndexOfRefractionRe:
    0: !!python/tuple [wl0,n0]
    1: !!python/tuple [wl1,n1]
    ...
  IndexOfRefractionIm:
    0: !!python/tuple [wl0,k0]
    1: !!python/tuple [wl1,k1]
    ...
Material2:
    ...
    
"Material1" and "Material2" are determined automatically by the filename of the CSV. If the CSV does not contain
a third column, only IndexOfRefractionRe will be written to the file.
"""

def csv_to_yaml(csv_file, yaml_file):
    # get filename without path or extension
    file_name = os.path.splitext(os.path.basename(csv_file))[0] 

    data_frame  = pd.read_csv(csv_file)

    # extract data
    wavelengths           = data_frame.iloc[:, 0].values
    refractive_index_real = data_frame.iloc[:, 1].values

    # create key for each csv file analyzed
    yaml_file.write(f"{file_name}:\n")
    yaml_file.write(f"  IndexOfRefractionRe:\n")

    for i in range(len(wavelengths)):
        yaml_file.write(f"    {i}: !!python/tuple [{wavelengths[i]},{refractive_index_real[i]}]\n")

    if len(data_frame.columns) > 2:
        # Extract the third column values if they exist
        refractive_index_imaginary = data_frame.iloc[:, 2].values
        yaml_file.write(f"  IndexOfRefractionIm:\n")
        for i in range(len(wavelengths)):
            yaml_file.write(f"    {i}: !!python/tuple [{wavelengths[i]},{refractive_index_imaginary[i]}]\n")
        

        

# Prompt the user for the folder path containing CSV files
folder_path = input("Enter the folder path containing CSV files: ")
yaml_file_name = input("Enter the output YAML file name: ")

yaml_file = open(yaml_file_name, 'w')

# Iterate through all CSV files in the folder and convert them to YAML
for file in os.listdir(folder_path):
    if file.endswith(".csv"):
        csv_file = os.path.join(folder_path, file) # full file path
        csv_to_yaml(csv_file, yaml_file)


