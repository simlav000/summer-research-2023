import numpy as np
import matplotlib.pyplot as plt
import h5py
from datetime import datetime

simFile = input("Enter file: ")

with h5py.File(simFile, 'r') as hdf:

    Flags = np.array(hdf.get("Flags").get("Flags"))
    DetectedPos = np.array(hdf.get("DetectedPos").get("DetectedPos"))
    MetaData = dict()
    
    for key, value in hdf.attrs.items():
        if isinstance(value, bytes):
            MetaData[key] = value.decode()
        else:
            MetaData[key] = value


TotalPhotons = len(Flags)
NumDetected = len(DetectedPos)
FractionDetected = NumDetected / TotalPhotons

def separatePointsByFace(Points):
    Length = 20.9 # mm
    Points = np.array(Points)  # Convert the list of points to a NumPy array

    x, y, z = Points[:, 0], Points[:, 1], Points[:, 2]
    
    WestMask = (x < -Length)
    BottomMask = (z < -Length)
    EastMask = (x > Length) 
    NorthMask = (y < -Length) 
    SouthMask = (y > Length)
    TopMask = (z > Length)
    
    PackagedCube = [
        [y[WestMask], z[WestMask]],
        [y[BottomMask],-x[BottomMask]],
        [-y[EastMask], z[EastMask]],
        [-x[NorthMask], z[NorthMask]],
        [z[SouthMask], x[SouthMask]],
        [x[TopMask], y[TopMask]]
    ]
    return PackagedCube
   
def plotLightMap(Style="contour"):
    DetectedFaces = separatePointsByFace(DetectedPos)

    # Define the dimensions of the square (ranging from -25 to +25)
    x_min, x_max = -25, 25
    z_min, z_max = -25, 25

    # Define the number of bins in the heatmap
    num_bins = 350

    face_names = ['West', 'Bottom', 'East', 'North', 'South', 'Top']
    cmap = 'plasma'  # Use 'plasma' colormap for more colors
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    contour_data = []
    histogram_data = []
    
    for face_index, face_name in enumerate(face_names):
        face_data = DetectedFaces[face_index]
        dim1 = face_data[0]
        dim2 = face_data[1]

        ax = axes[face_index // 3, face_index % 3]
        ax.grid(linewidth=0)
        if face_name == "West":
            ax.set_xticks([z_min, z_max])
            ax.set_ylabel('Location (mm)')
            ax.grid(linewidth=0)
        elif face_name == "North":
            ax.set_yticks([x_min, x_max])
            ax.set_xlabel("Location (mm)")
            ax.grid(linewidth=0)
        else:
            ax.set_xticks([])  # Remove x-axis tick labels
            ax.set_yticks([])
            ax.set_xlabel('')  # Remove labels too
            ax.set_ylabel('')
            ax.grid(False)
        if Style.lower() == "contour":
            # Create the 2D histogram
            H, xedges, yedges = np.histogram2d(dim1, dim2, bins=num_bins, range=[[x_min, x_max], [z_min, z_max]])
            contour_data.append((H, xedges, yedges))
        elif Style.lower() == "histogram":
            # Create the 2D histogram using hist2d()
            counts, xedges, yedges, im = ax.hist2d(dim1, dim2, bins=num_bins, range=[[x_min, x_max], [z_min, z_max]], cmap=cmap)
            histogram_data.append((counts, xedges, yedges))

    if Style.lower() == "contour":
        Heights = [H for H, _, _ in contour_data]
        Heights_flattened = [value for sublist in Heights for value in sublist]
        Max = np.max(Heights_flattened)

        for face_index, face_name in enumerate(face_names):
            face_data = contour_data[face_index]
            H = face_data[0]
            xedges = face_data[1]
            yedges = face_data[2]
            H_norm = H / Max

            ax = axes[face_index // 3, face_index % 3]  # Get the corresponding axis
            ax.grid(linewidth=0)
            ax.set_title(f'{face_name}')
            cf = ax.contourf(xedges[:-1], yedges[:-1], H_norm.T, cmap=cmap, vmin=0, vmax=1)
            ax.grid()
            
    elif Style.lower() == "histogram":
        counts = [counts for counts, _, _ in histogram_data]
        counts_flattened = [value for sublist in counts for value in sublist]
        Max = np.max(counts_flattened)
        for face_index, face_name in enumerate(face_names):
            face_data = histogram_data[face_index]
            counts = face_data[0]
            xedges = face_data[1]
            yedges = face_data[2]
            
            # Normalize the counts manually to [0, 1]
            counts_norm = counts / Max
            
            ax = axes[face_index // 3, face_index % 3]  # Get the corresponding axis
            ax.grid(linewidth=0)
            ax.set_title(f'{face_name}')
            # Plot the heatmap
            cf = ax.imshow(counts_norm.T, cmap=cmap, origin='lower', extent=[x_min, x_max, z_min, z_max], aspect='auto') 
            ax.grid()
            
    plt.tight_layout()

    # Get the current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Set the figure label (title) with improved spacing
    fig.suptitle(f"LoLX Detected Photon Heatmap", fontsize=16, y=0.95)

    # Add the FractionDetected as a subtitle at the bottom of the figure
    fig.text(0.5, 0.03, f"Photons Simulated: {format(TotalPhotons, ',')}\nPhotons Detected: {format(NumDetected, ',')}\nFraction Detected: {FractionDetected:.2f}", ha='center', fontsize=12)

    # Add color bar on the right of all subplots with enough whitespace
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
    cbar = plt.colorbar(cf, cax=cbar_ax)
    cbar.set_label('Light Intensity (Normalized)')  # Updated label

    # Adjust the spacing around the subplots and the figure edges
    plt.subplots_adjust(left=0.07, right=0.9, top=0.88, bottom=0.13)

    # Save the figure with the current date and time in the filename and increase the resolution (dpi)
    filename = f"/home/slavoie/Images/heatmap_{current_datetime}.png"
    plt.savefig(filename, dpi=500)
    plt.show()  

plotLightMap("histogram")
