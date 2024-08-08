from cocoapi.PythonAPI.pycocotools.coco import COCO
import enum
import requests
import os
import hashlib


def download_images(file_path):
    '''
    Downloads images from the COCO dataset to a local directory
    '''
    # initialize COCO api for instance annotations
    global coco
    coco = COCO(file_path)
    imgs = coco.loadImgs(coco.imgs)

    for img in imgs:
       coco.download_and_cache_images(coco.cache_dir, img['coco_url'], img['file_name'])
    # TODO add return control to share success or failure of download with list of images that failed to download
   

def save_file(file, save_directory):
    '''
    Saves a file to a specified directory
    '''
    os.makedirs(save_directory, exist_ok=True)
    file_path = os.path.join(save_directory, file.filename)
    file.save(file_path)
    return file_path