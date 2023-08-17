import os
import numpy as np
import pandas as pd

'''
This script is meant to take in as input the path to a directory holding files which contain
wavelength-dependent optical properties. It outputs a file with said optical properties formatted
in a manner readable by chroma.

The CSV's should be formatted according to the following two supported header styles:

1: wl,property,,"source"

    where wl is the wavelength (in nm), the properties include (but are not limited to):
      - Detection
      - IndexOfRefractionRe
      - ScatteringLength (in mm) <- ALL LENGTHS BUT WAVELENGTHS SHOULD BE mm
      - ...
    and the source is written between quotes. It is optional
    
2: wl,n,k,"source"

    where wl is the wavelength (in nm), n and k are the real and imaginary parts of the refractive 
    index, respectively. The source is optional.

Ensure the data has the correct units

'''

def sanitize_key(key):
    # Remove whitespaces and special characters to form valid YAML keys
    # Ideally, the user sticks to naming their property in the CSV to whatever the YAML
    # recognizes, for instance: AbsorptionLength, SpecularReflectivity, IndexOfRefractionRe, etc.
    # If this is not done, at least we have this.
    return "".join(c if c.isalnum() else "" for c in key)


def csv_to_yaml(csv_file, yaml_file):
    file_name = os.path.splitext(os.path.basename(csv_file))[0]

    data_frame = pd.read_csv(csv_file)

    header = data_frame.columns.tolist()
    prop_name = sanitize_key(header[1])  # Use the second column header as property name
    source = header[-1] if len(header) > 3 else None  # Source optional

    wavelengths = data_frame.iloc[:, 0].values
    property_values = data_frame.iloc[:, 1].values


    if source:
        yaml_file.write(f"# source: {source}\n")

    yaml_file.write(f"{file_name}:\n")

    if prop_name.lower() in ["n", "indexofrefractionre"]:
        yaml_file.write(f"  IndexOfRefractionRe:\n")
    else:
        yaml_file.write(f"  {prop_name}:\n")

    for i in range(len(wavelengths)):
        # Format wavelength and property value with proper precision (e.g., scientific notation)
        yaml_file.write(f"    {i}: !!python/tuple [{wavelengths[i]:.6e}, {property_values[i]:.6e}]\n")

    if len(header) > 2:
        # Extract the third column values if they exist
        refractive_index_imaginary = data_frame.iloc[:, 2].values
        if any(np.isnan(np.array(refractive_index_imaginary))):
            pass # deals with case where source is provided increasing length of header
                 # but no data is present at the third column
        else:   
            yaml_file.write(f"  IndexOfRefractionIm:\n")
            for i in range(len(wavelengths)):
                yaml_file.write(f"    {i}: !!python/tuple [{wavelengths[i]:.6e}, {refractive_index_imaginary[i]:.6e}]\n")


# Prompt the user for the folder path containing CSV files
folder_path = input("Enter the folder path containing CSV files: ")
yaml_file_name = input("Enter the output YAML file path/name: ")

with open(yaml_file_name, 'w') as yaml_file:
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            csv_file = os.path.join(folder_path, file)  # full file path
            csv_to_yaml(csv_file, yaml_file)
