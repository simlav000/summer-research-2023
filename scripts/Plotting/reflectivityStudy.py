import numpy as np
import h5py
import yaml
import matplotlib.pyplot as plt

'''
Author: Simon Lavoie 
simon.lavoie@mail.mcgill.ca
Summer 2023

This script is intended to be used to test the reflectivity of materials assigned to 
components within simulations. The idea is to load the geometry found under
[ChromaPath]/Geometry/ReflectivityStudy/ with the mountedLaser generation method.
This generation method defines a laser moving along the inner surface of the sphere
present in the stated geometry, pointing towards the origin. This results in
photons with incident angles ranging from 0 to 90 degrees. These angles are plotted 
against the fraction of photons which were reflected for each source (each source 
defines a different incident angle). The incident angles are computed assuming
the proper geometry is used.'''

yaml_path = "//home//slavoie//LoLX//chroma-simulation//Yaml//LoLX//LoLXReflectivityStudy.yaml"

file_path = input("Enter simulation file: ")

with h5py.File(file_path, 'r') as hdf:
    FlagsGroup = hdf.get("Flags")
    Flags = np.array(FlagsGroup.get("Flags"))
    NumDetectedGroup = hdf.get("NumDetected")
    NumDetected = np.array(NumDetectedGroup.get("NumDetected"))
    OriginGroup = hdf.get("Origin")
    Origin = np.array(OriginGroup.get("Origin"))
    PhotonWavelengthGroup = hdf.get("PhotonWavelength")
    PhotonWavelength = np.array(PhotonWavelengthGroup.get("PhotonWavelength"))

# assuming that each wavelength is the same 
Wavelength = PhotonWavelength[0]    
NumSources = len(NumDetected)
TotalPhotons = len(Flags)
PhotonsPerSource = TotalPhotons / NumSources

# Load refractive index values directly from yaml
yaml_file = yaml.load(open(yaml_path, 'r'), Loader=yaml.FullLoader)

# determine relevant materials
SheetMaterial = yaml_file["Components"]["Sheet"]["Surface"][0]
OutsideMaterial = yaml_file["Components"]["Sheet"]["Outside"][0]

# extract refractive indices
OpticalProperties = yaml.load(open(yaml_file["Detector"]["OpticalProperties"], "r"), Loader=yaml.FullLoader)
OutsideIndexDataReal = OpticalProperties[OutsideMaterial]["IndexOfRefractionRe"]
SurfaceIndexDataReal = OpticalProperties[SheetMaterial]["IndexOfRefractionRe"]
try:
    OutsideIndexDataImaginary = OpticalProperties[OutsideMaterial]["IndexOfRefractionIm"]
    OutsideHasImaginaryComponent = True
except KeyError:
    OutsideHasImaginaryComponent = False
    k1 = 0

try:
    SurfaceIndexDataImaginary = OpticalProperties[SheetMaterial]["IndexOfRefractionIm"]
    SurfaceHasImaginaryComponent = True
except KeyError:
    SurfaceHasImaginaryComponent = False
    k2 = 0
    
# Refractive index data can either be wavelength dependent or single-valued
if isinstance(OutsideIndexDataReal, dict):
    
    for index, tuples in enumerate(OutsideIndexDataReal.values()):
        if tuples[0] == Wavelength:
            n1 = tuples[1]
            if OutsideHasImaginaryComponent:
                k1 = list(OutsideIndexDataImaginary.values())[index][1]
else:
    n1 = OutsideIndexDataReal
    if OutsideHasImaginaryComponent:
        k1 = OutsideIndexDataImaginary

if isinstance(SurfaceIndexDataReal, dict):
    for index, tuples in enumerate(SurfaceIndexDataReal.values()):
        if tuples[0] == Wavelength:
            n2 = tuples[1]
            if SurfaceHasImaginaryComponent:
                k2 = list(SurfaceIndexDataImaginary.values())[index][1]
else:
    n2 = SurfaceIndexDataReal
    if SurfaceHasImaginaryComponent:
        k2 = SurfaceIndexDataImaginary
        

# Assuming proper geometry is loaded:
def getAOI(xCoordinate):
    SphereRadius = 152.6
    return np.arcsin(xCoordinate / SphereRadius) * 180 / np.pi

AOI = np.array([getAOI(xCoordinate) for xCoordinate in Origin[:, 0]])

# Each source will have a unique incident angle, and therefore unique reflectivity
FlagsSplitBySource = np.split(Flags, NumSources)

Reflectivity = []
for Source in FlagsSplitBySource:
    NumReflected = 0
    for Flag in Source:
        if Flag == 68: # SURFACE_DETECT + REFLECT_SPECULAR
            NumReflected += 1
    Reflectivity.append(NumReflected)
Reflectivity = np.array(Reflectivity) / PhotonsPerSource # Get fraction reflected

def reflecivity_s(incident_angle, z1, z2, epsilon_1, epsilon_2):
    incident_angle = np.array(incident_angle) / 180 * np.pi
    cos_transmitted_angle = np.sqrt(1 - (epsilon_1 / epsilon_2) * np.sin(incident_angle) ** 2 )
    return abs((z2 * np.cos(incident_angle) - z1 * cos_transmitted_angle) / (z2 * np.cos(incident_angle) + z1 * cos_transmitted_angle)) ** 2

def reflecivity_p(incident_angle, z1, z2, epsilon_1, epsilon_2):
    incident_angle = np.array(incident_angle) / 180 * np.pi
    cos_transmitted_angle = np.sqrt(1 - (epsilon_1 / epsilon_2) * np.sin(incident_angle) ** 2 )
    return abs((z2 * cos_transmitted_angle - z1 * np.cos(incident_angle)) / (z2 * cos_transmitted_angle + z1 * np.cos(incident_angle))) ** 2

incident_angles = AOI

#else:
# define constants
epsilon_0 = 8.854e-12
mu_0 = 4 * np.pi * 1e-7
characteristic_impedance_0 = np.sqrt(mu_0 / epsilon_0)
n1 = n1 + 1j * k1
n2 = 1.05 + 1j * 1.5
epislon_1 = np.real(n1) ** 2 - np.imag(n1) ** 2 + 2j * np.real(n1) * np.imag(n1)
characteristic_impedance_1 = characteristic_impedance_0 / np.sqrt(epislon_1) # z1
epsilon_2 = np.real(n2) ** 2 - np.imag(n2) ** 2 + 2j * np.real(n2) * np.imag(n2)
characteristic_impedance_2 = characteristic_impedance_0 / np.sqrt(epsilon_2) # z2
R_theory_s = reflecivity_s(incident_angles, characteristic_impedance_1, characteristic_impedance_2, epislon_1, epsilon_2)
R_theory_p = reflecivity_p(incident_angles, characteristic_impedance_1, characteristic_impedance_2, epislon_1, epsilon_2)   

# assuming randomly polarized photons, the result tends to being halfway between total s and p polarizations
Average = (R_theory_p + R_theory_s) / 2

# Calculate residuals
residuals = Reflectivity - Average

# Create a figure with subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

# Plot scatter plot of simulated reflectivity
plt.suptitle("Reflectivity Comparison Plot")
ax1.scatter(AOI, Reflectivity, c="b", s=10, label=fr"Simulated Reflectivity ($n_2$ = {np.real(n2)} + {np.imag(n2)}i, $\lambda$ = {Wavelength} nm)")
ax1.plot(incident_angles, R_theory_s, c="#3900bf", label="Theoretical Reflectivity (S-Polarization)")
ax1.plot(incident_angles, R_theory_p, c="#00a3bf", label="Theoretical Reflectivity (P-polarization)")
ax1.plot(incident_angles, Average, c="r", label="Average")
ax1.set_xlabel("Angle of Incidence (Degrees)")
ax1.set_ylabel("Reflectivity")
ax1.legend(loc="upper left")

# Plot scatter plot of residuals
ax2.scatter(AOI, residuals, c="b", s=10, label="Residuals")
ax2.set_xlabel("Angle of Incidence (Degrees)")
ax2.set_ylabel("Residuals\n(Simulation - Average)")
ax2.legend(loc="upper right")

# Adjust spacing between subplots
plt.tight_layout()

plt.show()
