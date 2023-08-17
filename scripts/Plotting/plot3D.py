import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import h5py
import os
from stl import mesh
import yaml
from matplotlib.colors import LinearSegmentedColormap

'''
Author: Simon Lavoie
simon.lavoie@mail.mcgill.ca
Summer 2023

This script is intended to be used in conjunction with the geometry found at 
[ChromaPath]/Geometry/ReflectivityStudy/
It is used to visualize final photon positions overlaid on top of the geometry.
It was made to ensure the guidedLaser() and mountedLaser() generation methods
worked properly. The geometry plotted by this function is found from within the 
YAML card, meaning you can turn off the Sheet by excluding it from the YAML (even
if it was present when the simulation was run).
Photon positions are plotted on a color gradient from white to red to black based
on when they were generated.
Source origins are plotted as black "X's".

'''
# Yaml card to know what geometry is relevant
yaml_card = "/home/slavoie/LoLX/chroma-simulation/Yaml/LoLX/LoLX.yaml"

file_path = input("Enter path of file to visualize: ")

with h5py.File(file_path, 'r') as hdf:
    FinalPostitionGroup = hdf.get("FinalPosition")
    FinalPosition = np.array(FinalPostitionGroup.get("FinalPosition"))
    x_finalPos = FinalPosition[:, 0]
    y_finalPos = FinalPosition[:, 1]
    z_finalPos = FinalPosition[:, 2]
    OriginGroup = hdf.get("Origin")
    Origins = np.array(OriginGroup.get("Origin"))

# Create a figure and a 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Define a custom colormap from white to red to black
colors = np.linspace(0, 1, len(x_finalPos))
cmap = LinearSegmentedColormap.from_list('CustomColormap', ['white', 'red', 'black'])

# Plot the final positions with the color gradient
#sc = ax.scatter(x_finalPos, y_finalPos, z_finalPos, c=colors, cmap=cmap, marker='o', label="FinalPosition")

# Plot the origin as a black 'x'
ax.scatter(Origins[:, 0], Origins[:, 1], Origins[:, 2], c='lime', marker='x', label="Origin")

# Set colorbar properties
#cbar = plt.colorbar(sc, ax=ax)
#cbar.set_label('Earliest to Latest Photon')

# Keep track of largest points to plot to scale axes later
Largest_x = 0
Largest_y = 0
Largest_z = 0

# Load YAML data
with open(yaml_card, "r") as yaml_card:
    yaml_data = yaml.safe_load(yaml_card)
    # Directory containing STL files
    if "ChromaPath" in yaml_data:
        ChromaPath = yaml_data["ChromaPath"]
        PathToDetector = yaml_data["Detector"]["PathToDetector"]
        directory = ChromaPath.join(PathToDetector.split("[ChromaPath]"))
    else:
        directory = yaml_data["Detector"]["PathToDetector"]

    components = yaml_data["Components"]

    # Loop over all files in the directory
    for i, filename in enumerate(os.listdir(directory)):
        if os.path.splitext(filename)[0] in components:
            if filename not in ["Tube.stl", "Cage.stl"]: #Don't want to see them
                # Load the STL file
                stl_file = os.path.join(directory, filename)
                mesh_data = mesh.Mesh.from_file(stl_file)

                # Get the vertices of the triangles
                vertices = mesh_data.vectors.reshape(-1, 3)

                # Extract x, y, z coordinates
                x = vertices[:, 0]
                y = vertices[:, 1]
                z = vertices[:, 2]

                for i in range(len(x)):
                    if x[i] > Largest_x:
                        Largest_x = x[i]
                    
                    if y[i] > Largest_y:
                        Largest_y = y[i]
                    
                    if z[i] > Largest_z:
                        Largest_z = z[i]

                # Assign colors based on file index
                if filename == "Sphere.stl":
                    color = 'blue'
                    alpha = 0.01
                elif filename not in ["FBK_Packages.stl", "HPK_Packages", "Photocathode.stl", "PMT_Body.stl", "PMT_Body.stl", "PMT_Support.stl", "Tiles.stl"]:
                    color = "red"
                    alpha = 1
                else:
                    color = np.random.rand(3,)  # Random RGB color
                    alpha = 0.0001

                # Plot the points with the assigned color
                ax.scatter(x, y, z, color=color, marker='o', alpha=alpha)

                # For geometry files with few vertices (e.g a rectangular prism),
                # plotting the vertices as points is insufficient and so a mesh
                # is painstakingly defined to fill the empty space
                if filename == "Sheet.stl":
                    rect_vertices = np.array([
                        [min(x), min(y), min(z)], # index 0
                        [max(x), min(y), min(z)], # index 1
                        [max(x), max(y), min(z)], # so on...
                        [min(x), max(y), min(z)],
                        [min(x), min(y), max(z)],
                        [max(x), min(y), max(z)],
                        [max(x), max(y), max(z)],
                        [min(x), max(y), max(z)]
                    ])

                    # The following faces are triangles defined by manually
                    # connecting vertices together. Each number in these 
                    # arrays refer to indices as defined above.
                    rect_faces = np.array([
                        [0, 3, 7],  # side
                        [0, 4, 7],  # side
                        [0, 4, 5],  # front
                        [0, 1, 5],  # front
                        [1, 5, 6],  # side
                        [1, 2, 6],  # side
                        [3, 7, 6],  # back
                        [3, 2, 6],  # back
                        [0, 3, 2],  # bottom
                        [0, 1, 2],  # bottom
                        [4, 7, 6],  # top
                        [4, 5, 6]  # top
                    ])

                    ax.plot_trisurf(rect_vertices[:, 0], rect_vertices[:, 1], rect_vertices[:, 2], triangles=rect_faces,
                                    facecolor="#A09E00", alpha=0.1)
                
Range = np.max([Largest_x, Largest_y, Largest_z])
                
# Fix aspect ratio
ax.set_xlim(-Range, Range)
ax.set_ylim(-Range, Range)
ax.set_zlim(-Range, Range)



# Set labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('STL Files Reconstruction')

plt.legend(loc="lower left")
# Show the plot
plt.show()
