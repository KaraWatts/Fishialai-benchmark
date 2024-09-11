from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text, Float, UniqueConstraint, Boolean, LargeBinary, text
import enum
import requests
from utilities import fish_detection, compare_results, send_feedback, save_file, download_images, get_token, fetch_image_url, submit_image ,create_database_if_not_exists, get_coco_instance, database_url, cache, staging_secret, staging_ID, prod_ID, prod_secret
import json


# Initialize Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
app.config['CACHE_TYPE'] = 'simple'  # Use a simple in-memory cache
cache.init_app(app)


# Check if local database exists/ create it if not - on application startup
with app.app_context():
    create_database_if_not_exists()

# Set SQLAlchemy Database URI from environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create SQLAlchemy database instance
db = SQLAlchemy(app)


class StageOrProductionEnum(enum.Enum):
    '''
    Enum class for stage or production environment.

    Attributes:
        Stage (str): Stage environment.
        Production (str): Production environment
    '''
    Stage = "Stage"
    Production = "Production"


class BenchmarkRun(db.Model):
    '''
    SQLAlchemy model for the benchmark run table.

    This model represents a benchmark run with various attributes related to the COCO dataset and 
    API performance metrics.

    Attributes:
        id (int): Unique identifier for the benchmark run.
        coco_image_id (int): ID of the COCO image associated with this benchmark run.
        dev_api_version (str): Version of the development API used during the benchmark.
        stage_or_production (str): Indicates whether the benchmark was run in a staging or production environment.
        run_datetime (datetime): Date and time when the benchmark was executed.
        coco_species_common_name (str): Common name of the species from the COCO dataset.
        coco_species_genus (str): Genus name of the species from the COCO dataset.
        dev_api_results_json (str): JSON string containing the results from the development API.
        endpoint_execute_time (float): Time taken to execute the API endpoint, in seconds.
    '''

    __tablename__ = 'benchmark_run'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coco_image_id = Column(Integer, nullable=False)
    dev_api_version = Column(String(255), nullable=False)
    stage_or_production = Column(Enum(StageOrProductionEnum), nullable=False)
    run_datetime = Column(DateTime, nullable=False)
    coco_species_common_name = Column(String(255))
    coco_species_genus = Column(String(255))
    match = Column(Boolean, nullable=False)
    match_accuracy = Column(Float)
    dev_api_results_json = Column(LargeBinary)
    endpoint_execute_time = Column(Float)

    __table_args__ = (
        UniqueConstraint('coco_image_id', 'dev_api_version', 'stage_or_production', 'run_datetime', name='unique_key_index'),
    )

# Create tables
with app.app_context():
    db.create_all()
    print("Tables created successfully!")


# Attempting to increase max allowed packet size for MySQL to accomodate large json data
with app.app_context():
    db.session.execute(text("SET GLOBAL max_allowed_packet = 1116777216"))
    db.session.commit()
    print("max_allowed_packet updated to 16MB.")



# Test Object for route testing
route_test_data = {'data': "Test Successful"}

@app.route("/test", methods=("GET",))
def test_data():
    '''
    Test route to check if the server is running

    Parameters:
    None

    Returns:
    JSON response: test data
    '''
    return jsonify(route_test_data)


@app.route('/upload_test_data', methods=['POST'])
def upload_test_data():
    '''
    Save Coco file data to local directory

    Parameters:
    None

    Returns:
    success message or error message
    '''
    # Check if the request contains a file
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



@app.route('/get_token/<environment>', methods=['GET'])
def fetch_token(environment):
    '''
    Call on Fetch Access Token Function

    Parameters:
    environment: str

    Returns:
    JSON response: success message or error message
    '''
    # Submit api request to get token
    token = get_token(environment)
    if token:
        return jsonify({'message': 'Access token obtained successfully'}), 200
    else:
        return jsonify({'error': 'Failed to obtain token'}), 500



@app.route('/image_url/<environment>/<image_id>', methods=['POST'])
def submit_image_with_feedback(environment, image_id):
    '''
    Full API call test series for Fishial API
    1. Fetch image URL
    2. Upload image to Fishial API
    3. Request fish detection
    4. Send feedback - agree or disagree with feedback - based on response match to test data

    Parameters:
    environment: str
    image_id: str

    Returns:
    JSON response: success message or error message
    '''

    try:
        # submit image data to Fishial API to receive image url
        image_url_data = fetch_image_url(environment, image_id)
        # upload image to Fishial API using image url
        submit_image(image_url_data)
        # request fish detection from Fishial API
        detection_results = fish_detection(environment, image_url_data)
        # store detection results in database
        prepare_submit_detection_data(detection_results, image_id, environment)
        # compare results from Fishial API to test data
        match = compare_results(detection_results, image_id, environment)
        # send match results feedback to Fishial API
        send_feedback(match)

        return jsonify({'message': 'Full image submission with feedback completed succesfully'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def prepare_submit_detection_data(detection_results, image_id, environment):
    coco = get_coco_instance()
    print(detection_results['results'][0]['species'])
    image_id = int(image_id)
    coco_scientific_name = None
    results = detection_results['results'][0]['species']
    match = False
    image_data = coco.imgToAnns[image_id]
    if len(image_data) > 1:
        category_id = image_data[1]['category_id']
        coco_scientific_name = coco.cats[category_id]['supercategory']
        for species in results:
            if species['name'] == coco_scientific_name:
                match = True
                break
    detection_results = json.dumps(detection_results).encode('utf-8')

    coco_data = {
        'image_id': image_id,
        'scientific_name': coco_scientific_name,
        'comparison_results': match
    }
    # Record fish detection data to database
    record_fish_detection_data(coco_data, detection_results, environment)


import datetime

def record_fish_detection_data(coco_data, fish_detection_data, environment):
    '''
    Record fish detection data to database
    '''
    pass

    # Record fish detection data to database
    new_test_run = BenchmarkRun(
        coco_image_id=coco_data['image_id'],
        dev_api_version='v1',
        stage_or_production=environment,
        run_datetime=datetime.datetime.now(),
        coco_species_genus=coco_data['scientific_name'],
        match=coco_data['comparison_results'],
        dev_api_results_json=fish_detection_data, 
        endpoint_execute_time=0.5
    )

    db.session.add(new_test_run)
    db.session.commit()

    test_results = check_benchmark(coco_data['image_id'])
    print(test_results)

def check_benchmark(coco_image_id):
    record = BenchmarkRun.query.filter_by(coco_image_id=coco_image_id).order_by(BenchmarkRun.run_datetime.desc()).first()
    
    if record:
        return (
            'id', record.id,
            'coco_image_id', record.coco_image_id,
            'dev_api_version', record.dev_api_version,
            'stage_or_production', record.stage_or_production.name,
            'run_datetime', record.run_datetime.isoformat(),
            'coco_species_genus', record.coco_species_genus,
            'match', record.match,
            'endpoint_execute_time', record.endpoint_execute_time
        )
    else:
        return jsonify({'message': 'Record not found'}), 404



#TODO - set up image data to be found by image id - can find individual image or loop through all
#TODO - need to combine with coco.py files to get image data



        
if __name__ == "__main__":
    app.run(debug=True, port=8080)
