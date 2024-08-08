from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Enum, DateTime, Text, Float, UniqueConstraint
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from flask_caching import Cache
from cocoapi.PythonAPI.pycocotools.coco import COCO
import enum
import requests
import os
import hashlib
import save_file from backend.util

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
app.config['CACHE_TYPE'] = 'simple'  # Use a simple in-memory cache
cache = Cache(app)
coco = None

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

# Check if local database exists/ create it if not - on application startup
with app.app_context():
    create_database_if_not_exists()

#Pulling the client ID and secret from the environment variables
staging_ID = os.getenv('STAGING_ID')
staging_secret = os.getenv('STAGING_SECRET')
prod_ID = os.getenv('PROD_ID')
prod_secret = os.getenv('PROD_SECRET')
access_token = None

# Set SQLAlchemy Database URI from environment variable
database_url = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create SQLAlchemy database instance
db = SQLAlchemy(app)

# Define enum for stage or production
class StageOrProductionEnum(enum.Enum):
    Stage = "Stage"
    Production = "Production"

# Define SQLAlchemy model for benchmark run
class BenchmarkRun(db.Model):
    __tablename__ = 'benchmark_run'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coco_image_id = Column(Integer, nullable=False)
    dev_api_version = Column(String(255), nullable=False)
    stage_or_production = Column(Enum(StageOrProductionEnum), nullable=False)
    run_datetime = Column(DateTime, nullable=False)
    coco_species_common_name = Column(String(255))
    coco_species_genius = Column(String(255))
    dev_api_results_json = Column(Text)
    endpoint_execute_time = Column(Float)

    __table_args__ = (
        UniqueConstraint('coco_image_id', 'dev_api_version', 'stage_or_production', 'run_datetime', name='unique_key_index'),
    )

data = {'data': "Test Successful"}

# test route
@app.route("/test", methods=("GET",))
def test_data():
    return jsonify(data)


# Download Images to local directory
def download_images(file_path):
    # initialize COCO api for instance annotations
    global coco
    coco = COCO(file_path)
    imgs = coco.loadImgs(coco.imgs)

    for img in imgs:
       coco.download_and_cache_images(coco.cache_dir, img['coco_url'], img['file_name'])
    # TODO add return control to share success or failure of download with list of images that failed to download
    


# Upload test data coco file
@app.route('/upload_test_data', methods=['POST'])
def upload_test_data():
    '''
    Save test data to local directory
    '''
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    
    # Get the file from the request
    file = request.files['file']
    # Check if the file is empty
    if file.filename == '':
        return jsonify({'message': 'No file selected for uploading'}), 400
    # Set the save directory for the file
    save_directory = 'annotations'
    
    try:
        # Save the file to the directory
        file_path = save_file(file, save_directory)
        # Download images from the COCO dataset and save to local directory
        download_images(file_path)
        # Return success message
        return jsonify({'message': 'File uploaded successfully!', 'filename': file.filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def verify_file_integrity(file_path, original_file_path):
    # Calculate checksums of both files and compare
    original_checksum = calculate_checksum(original_file_path)
    saved_checksum = calculate_checksum(file_path)
    
    return original_checksum == saved_checksum

def calculate_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
    




def get_token(environment):
    '''
    Fetch Access Token from Fishial API
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




@app.route('/get_token/<environment>', methods=['GET'])
@cache.cached(timeout=600, key_prefix='access_token') # cache the access token for 10 minutes
def fetch_token(environment):
    '''
    Call on Fetch Access Token Function
    '''
    token = get_token(environment)
    if token:
        return token
    else:
        return jsonify({'error': 'Failed to obtain token'}), 500



@app.route('/image_url/<environment>/<image_id>', methods=['POST'])
def request_image_url(environment, image_id):
    '''
    Request URL for image upload
    '''
    global coco
    if coco is None:
        return jsonify({'error': 'COCO is not initialized'}), 400
    
    if environment == 'stage':
        url = 'https://api.stage.fishial.ai/v1/recognition/upload'
    else:
        url = 'https://api.fishial.ai/v1/recognition/upload'

    # pull the access token from cache
    cachedToken = cache.get('access_token')
    if not cachedToken:
        return jsonify({'error': 'Access token not found'}), 500
    
    # use the access token to upload image
    headers = {
        'Authorization': f'Bearer {cachedToken}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    filename = coco.imgs[int(image_id)]['file_name']
    bytesize = os.path.getsize(f'images/{filename}')
    checksum = coco.imgs[int(image_id)]['checksum']
    data = {
        "blob": {
            "filename": filename,
            "content_type": "image/jpeg",
            "byte_size": bytesize,
            "checksum": checksum
            }
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to upload image'}), response.status_code


# upload image to Fishial API
@app.route('/upload_image', methods=['PUT'])
def upload_image():
    # Get data from request
    url = request.args.get('url')
    content_disposition = request.headers.get('Content-Disposition')
    content_md5 = request.headers.get('Content-Md5')
    content_type = request.headers.get('Content-Type')
    image_file = request.files['image']  # Assuming 'image' is the name of the file input field

    headers = {
        'Content-Disposition': 'inline; filename="fishpic.jpg"; filename*=UTF-8\'\'fishpic.jpg',
        'Content-Md5': 'EA5w4bPQDfzBgEbes8ZmuQ==',
        'Content-Type': ''  # Make sure to set the correct Content-Type if required
    }
    files = {'file': open(image, 'rb')}
    response = requests.put(url, headers=headers, files=files)
    
    if response.status_code == 200:
        print('File uploaded successfully.')
    else:
        print(f'Failed to upload file. Status code: {response.status_code}')

#TODO - set up image data to be found by image id - can find individual image or loop through all
#TODO - need to combine with coco.py files to get image data

        
if __name__ == "__main__":
    app.run(debug=True, port=8080)