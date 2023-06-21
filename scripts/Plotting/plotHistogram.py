import numpy as np
import h5py
import matplotlib.pyplot as plt
from scipy.stats import iqr
import math

path = '/home/slavoie/packages/data/nexo/test/histogramTest/chroma_nEXO_LARGE_230525_120046_r5750.h5'
with h5py.File(path, 'r') as hdf:
    keys = list(hdf.keys())

    # dictionary to store the extracted data
    extracted_data = {}

    # list of desired keys to extract data from
    keys_to_extract = ['NumDetected']

    # Loop over the keys and extract the data
    for key in keys_to_extract:
        group = hdf.get(key)
        extracted_data[key] = np.array(group.get(key))

    # Access the extracted data
    NumDetected = extracted_data['NumDetected']

# Determine the optimal number of bins
IQR = iqr(NumDetected)
maxCount = max(NumDetected)
minCount = min(NumDetected)
n = len(NumDetected)
h = 2 * IQR / (n ** (1/3))
binCount = int(np.floor((maxCount - minCount) / h))

# Compute mean and standard deviation
meanCount = np.mean(NumDetected)
sigmaCount = np.std(NumDetected)

totalNumberOfSimulatedPhotons = 10000 * 50000

# Plot histogram
plt.hist(NumDetected, bins=binCount, density=True, label=f"$\mu$ = {math.trunc(np.round(meanCount))}\n$\sigma$ = {math.trunc(np.round(sigmaCount))}", color="#972AA8")
plt.xlabel("Number of photons detected")
plt.ylabel("Proportion of occurences")
plt.title("Photon detection count histogram")
plt.legend(loc="upper right")
plt.show()
plt.savefig('/home/slavoie/packages/data/nexo/test/histogramTest/histogram.png')


