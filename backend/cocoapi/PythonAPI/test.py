# %matplotlib inline
from pycocotools.coco import COCO
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
import pylab
pylab.rcParams['figure.figsize'] = (8.0, 10.0)



annFile=f"../../annotations/Fishial_Export_May_13_2024_14_29_Prod_Export_Test_Images_for_testing(1).json"

# initialize COCO api for instance annotations
coco=COCO(annFile)