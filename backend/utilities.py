from flask import Flask, jsonify, request
from cocoapi.PythonAPI.pycocotools.coco import COCO
import requests
import os
from dotenv import load_dotenv
from cocoInstance import set_coco_instance, get_coco_instance
from flask_caching import Cache
import mysql.connector
from mysql.connector import Error
from flask_caching import Cache


"""
utilities.py

This module contains utility functions and helper classes used across the application.

Exceptions:
- `ImageDataError`: Base class for other exceptions.
- `InvalidImageIDFormatError`: Raised when the image ID format is invalid.
- `ImageNotFoundError`: Raised when the image is not found in the COCO dataset.
- `ImageFileNotFoundError`: Raised when the image file is not found on the filesystem.

Global Variables:
- `cache`: Cache object for caching data.

Environment Variables:
- `staging_ID`: Client ID for staging environment.
- `staging_secret`: Client secret for staging environment.
- `prod_ID`: Client ID for production environment.
- `prod_secret`: Client secret for production environment.
- `database_url`: URL for the MySQL database.

Functions:
- `get_cached_token`: Fetches the cached access token.
- `download_images`: Downloads images from the COCO dataset to a local directory.
- `save_file`: Saves a file to a specified directory.
- `get_token`: Fetches the access token from Fishial API and caches it for 10 minutes.
- `get_image_data`: Get image data from the COCO dataset.
- `fetch_image_url`: Fetches the URL for image upload from Fishial API.
- `create_database_if_not_exists`: Creates the database if it does not exist.

"""


class ImageDataError(Exception):
    """Base class for other exceptions"""
    pass

class InvalidImageIDFormatError(ImageDataError):
    """Raised when the image ID format is invalid"""
    pass

class ImageNotFoundError(ImageDataError):
    """Raised when the image is not found in the COCO dataset"""
    pass

class ImageFileNotFoundError(ImageDataError):
    """Raised when the image file is not found on the filesystem"""
    pass

'''Global Variables'''
# Initialize cache object
cache = Cache()

'''Environment Variables'''
# Load environment variables from .env file
load_dotenv()

#Pulling environment variables
staging_ID = os.getenv('STAGING_ID')
staging_secret = os.getenv('STAGING_SECRET')
prod_ID = os.getenv('PROD_ID')
prod_secret = os.getenv('PROD_SECRET')
database_url = os.getenv('DATABASE_URL')


'''Functions'''
def get_cached_token():
    '''
    Fetches the cached access token

    Returns:
    str: access token
    '''
    token = cache.get('access_token')
    if not token:
        raise Exception('Access token not found in cache')
    return token

def download_images(file_path):
    '''
    Downloads images from the COCO dataset to a local directory

    Parameters:
    file_path: str

    Returns:
    None
    '''
    # initialize COCO api for instance annotations
    set_coco_instance(file_path)
    coco = get_coco_instance()

    imgs = coco.loadImgs(coco.imgs)

    for img in imgs:
       coco.download_and_cache_images(coco.cache_dir, img['coco_url'], img['file_name'])
    # TODO add return control to share success or failure of download with list of images that failed to download
   

def save_file(file, save_directory):
    '''
    Saves a file to a specified directory

    Parameters:
    file: FileStorage
    save_directory: str

    Returns:
    str: File path of the saved file
    '''
    os.makedirs(save_directory, exist_ok=True)
    file_path = os.path.join(save_directory, file.filename)
    file.save(file_path)
    return file_path

@cache.cached(timeout=600, key_prefix='access_token') # cache the access token for 10 minutes
def get_token(environment):
    '''
    Fetch Access Token from Fishial API and caches it for 10 minutes

    Parameters:
    environment: str

    Returns:
    str: access token
    '''
    if environment == 'stage':
        url = 'https://api-users.stage.fishial.ai/v1/auth/token'
        client_id = staging_ID
        client_secret = staging_secret
    else:
        url = 'https://api-users.fishial.ai/v1/auth/token'
        client_id = prod_ID
        client_secret = prod_secret
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        token = response.json().get('access_token')
        return token
    else:
        return None
    

def get_image_data(coco, image_id):
    '''
    Get image data from coco dataset

    Parameters:
    coco: COCO instance
    image_id: int

    Returns:
    tuple: (filename, bytesize, checksum)

    Raises:
    InvalidImageIDFormatError: If image_id is not an integer.
    ImageNotFoundError: If the image is not found in the COCO dataset.
    ImageFileNotFoundError: If the image file is not found on the filesystem.
    '''
    try:
        # Ensure image_id is an integer and in coco.imgs
        image_id = int(image_id)
        if image_id not in coco.imgs:
            raise ImageFileNotFoundError('Image not found in COCO dataset')
        
        # Access the file_name and checksum from coco.imgs
        filename = coco.imgs[image_id]['file_name']
        checksum = coco.imgs[image_id]['checksum']
        
        # Check if the file exists and get its size
        file_path = f'images/{filename}'
        if not os.path.exists(file_path):
            raise ImageFileNotFoundError('Image file not found in local directory')
        
        # Get the size of the file
        bytesize = os.path.getsize(file_path)
        
        # Return the information in a JSON response
        return (filename, bytesize, checksum)
    
    except ValueError:
        raise InvalidImageIDFormatError('Invalid image ID format')
    except ImageDataError as e:
        raise e  # Re-raise custom exceptions
    except Exception as e:
        # Catch any unexpected errors and raise a generic exception
        raise ImageDataError(f'An unexpected error occurred: {str(e)}')
    


def fetch_image_url(url,image_id):
    '''
    Fetch URL for image upload from Fishial API

    Parameters:
    url: str
    image_id: int

    Returns:
    JSON response: image upload URL data or error message
    '''

    try:
        # Get the COCO instance
        coco = get_coco_instance()

        # Pull access token from cache
        cachedToken = get_cached_token()
        print(cachedToken)

        # Get image data from COCO dataset
        image_data = get_image_data(coco, image_id)
        filename, bytesize, checksum = image_data # unpack the tuple containing image data

        # Prepare headers for the request
        headers = {
            'Authorization': f'Bearer {cachedToken}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        # Prepare data for the request
        data = {
            "blob": {
                "filename": filename,
                "content_type": "image/jpeg",
                "byte_size": bytesize,
                "checksum": checksum
                }
        }

        # Send the image url request to Fishial API
        response = requests.post(url, headers=headers, json=data)
        return jsonify(response.json())

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


def create_database_if_not_exists():
    try:
        # Try to connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root'
        )
        
        # Check if the database exists
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES LIKE 'fishial_benchmark_db'")
        result = cursor.fetchone()
        
        if not result:
            # If database doesn't exist, execute setup.sql to create it
            with open('setup.sql', 'r') as file:
                setup_sql = file.read()
            cursor.execute(setup_sql)
            print("Database 'fishial_benchmark_db' created successfully!")
        else:
            print("Database 'fishial_benchmark_db' already exists.")

    except Error as e:
        print(f"Error connecting to MySQL server: {e}")

    finally:
        if 'connection' in locals() or 'connection' in globals():
            connection.close()
            cursor.close()

