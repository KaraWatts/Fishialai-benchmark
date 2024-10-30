# Fishial AI Benchmark Testing Suite

This project is a benchmarking tool for evaluating Fishial AI models, specifically designed to streamline the testing and validation process for new model versions. It allows users to upload labeled test datasets in COCO format, select the Fishial AI model they want to test, and compare the model’s predictions against expected results. The tool also performs regression testing by comparing new models with previous versions to confirm improvements and prevent regressions.

## Prerequisites

Before getting started, make sure you have the following installed:

- [Node.js](https://nodejs.org/en/download/) (with npm)
- [Python](https://www.python.org/downloads/) (with pip)
- [MySQL](https://dev.mysql.com/downloads/mysql/)
- [Git](https://git-scm.com/)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/KaraWatts/Fishialai-benchmark.git
cd fishialai-benchmark
```

### 2. MySQL Setup
1. **Install MySQL if not already installed.** Follow the [MySQL Installation Guide](https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/)
 for your operating system.


2. **Configure your database connection.**
In the backend directory, create a .env file with the following content, replacing the placeholders with your database details:

    ```bash
    DATABASE_URL='mysql+mysqlconnector://root:@localhost/fishial_benchmark_db'
    STAGING_ID=(insert staging environment ID)
    STAGING_SECRET=(insert staging environment secret key)
    PROD_ID=(insert production environment ID)
    PROD_SECRET=(insert production environment secret key)
    ```
### 2. Backend Setup (Flask)
1. **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2. **Set up a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Run the Flask server:**
    ```bash
    python main.py
    ```
By default, the backend server will start on http://127.0.0.1:5000.

### 3. Frontend Setup (React)
1. **Navigate to the frontend directory:**
    ```bash
    cd ../frontend
    ```
2. **Install dependencies:**
    ```bash
    npm install
    ```
3. **Run the React application:**
    ```bash
    npm run dev
    ```
By default, the frontend will start on http://localhost:3000.

## Backend API Endpoints
The backend API provides several endpoints to facilitate the upload, testing, and benchmarking of AI models.

| Method | Endpoint                  | Description                                |
|--------|----------------------------|--------------------------------------------|
| GET    | `/test`                    | Health check for the API                   |
| POST   | `/upload_test_data`        | Uploads COCO file and downloads images     |
| GET    | `/get_token/<env>`         | Retrieves an access token for Fishial API  |
| POST   | `/image_url/<env>/<id>`    | Retrieves image upload URL                 |
| PUT    | `/upload_image`            | Uploads an image to Fishial API            |


## End Goals

The application aims to provide users with an efficient and automated way to benchmark and evaluate fish identification AI models. The primary end goals are as follows:

1. **Upload COCO Test Data Files**: Users should be able to upload `.coco` files that contain labeled test data. Each file should specify expected results for each image, allowing for accurate comparison with model predictions.

2. **Select AI Model for Testing**: Users can choose the specific version of the Fishial AI model they want to test. The application will use this model to process each image in the COCO dataset and produce predictions for fish species identification.

3. **Model Evaluation and Comparison**: The app will run the selected AI model on the uploaded images and compare the model's results with the expected results from the COCO file. This ensures that the model meets performance expectations and accurately identifies species.

4. **Regression Testing**: The application will conduct a regression test by comparing the selected model's performance against the previous version of the model. This comparison ensures that any new model version improves upon or at least maintains the performance of the prior version, helping to prevent regressions.

By achieving these goals, the app will streamline the benchmarking and validation process, giving users a reliable tool for assessing and tracking model improvements over time.

## Key Technologies

- **Flask**: Provides the backend API for managing and processing model benchmark requests.
- **React**: Powers the frontend interface, allowing users to upload files, select models, and view results.
- **MySQL**: Stores historical benchmarking results for each model and image, enabling performance tracking over time.
- **[pycocotools**: Used to parse COCO-formatted datasets. The [pycocotools library](https://github.com/cocodataset/cocoapi/tree/master) allows the application to handle labeled datasets efficiently, facilitating image retrieval and comparison with expected results in the COCO format.


## Running the Full Application

After completing all set up above to start up the app just run the final start up commands for the frontend and the backend.

### Start the Flask backend (from the backend directory):
```bash
python main.py
```
### Start the React frontend (from the frontend directory):
```bash
npm run dev
```
Visit http://localhost:3000 in your browser to access the application. 

## Contributing
We welcome contributions to improve and expand the Fishial AI Benchmark Testing Suite! To contribute, please follow these steps:

1. **Fork the Repository:** Click on "Fork" at the top right of this page to create a copy of the repository under your GitHub account.

2. **Clone the Forked Repository:**
    ```
    git clone https://github.com/<your-username>/Fishialai-benchmark.git
    cd fishialai-benchmark
    ```
3. **Follow Setup Instructions from step 2:** [Return to Setup section](#setup)

4. **Create a New Branch:** Use a descriptive branch name that reflects your changes.
    ```
    git checkout -b feature/your-feature-name
    ```
5. **Make Your Changes and Submit a Pull Request:** Implement the changes or features you wish to add, adhering to the code style and include clear commit messages. Ensure Pull request is detailed, including screenshots for any changes to the UI.

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

## Contact
For questions, issues, or feedback, please feel free to open an issue on GitHub or reach out directly.

**Happy Testing!**