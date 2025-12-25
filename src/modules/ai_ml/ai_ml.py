"""
AI/ML Module
Handles machine learning model management, experiment tracking, data pipeline tools, and MLOps integration
"""
import sys
import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator
class AIMLTools:
    """Handles AI and Machine Learning tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def setup_ml_project(self) -> None:
        """Help set up a machine learning project structure"""
        print("\n" + "="*70)
        print("MACHINE LEARNING PROJECT SETUP")
        print("="*70)

        print("\nThis tool helps create a standard ML project structure.")

        project_name = input("Enter project name: ").strip()
        if not project_name:
            print("Project name cannot be empty!")
            input("\nPress Enter to continue...")
            return

        # Validate project name
        if not self.validator.validate_file_name(project_name):
            print("Invalid project name!")
            input("\nPress Enter to continue...")
            return

        # Create project directory
        project_dir = Path(project_name)
        if project_dir.exists():
            print(f"Project directory '{project_name}' already exists!")
            input("\nPress Enter to continue...")
            return

        project_dir.mkdir()

        # Create standard ML project structure
        dirs_to_create = [
            project_dir / "data",
            project_dir / "data" / "raw",
            project_dir / "data" / "processed",
            project_dir / "data" / "external",
            project_dir / "notebooks",
            project_dir / "src",
            project_dir / "src" / "data",
            project_dir / "src" / "features",
            project_dir / "src" / "models",
            project_dir / "src" / "visualization",
            project_dir / "models",
            project_dir / "reports",
            project_dir / "reports" / "figures",
            project_dir / "tests",
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)

        # Create requirements.txt
        requirements_content = '''# Core scientific computing
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0

# Machine learning
scikit-learn>=1.0.0
xgboost>=1.5.0
lightgbm>=3.3.0

# Deep learning (optional)
# tensorflow>=2.8.0
# pytorch>=1.11.0
# torchvision>=0.12.0

# Visualization
matplotlib>=3.4.0
seaborn>=0.11.0
plotly>=5.0.0

# Data processing
# dask>=2022.2.0
# sqlalchemy>=1.4.0

# Experiment tracking
mlflow>=1.20.0
# wandb>=0.12.0

# Utilities
tqdm>=4.60.0
click>=8.0.0
python-dotenv>=0.19.0

# Development
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
jupyter>=1.0.0
'''

        with open(project_dir / "requirements.txt", "w") as f:
            f.write(requirements_content)

        # Create setup.py
        setup_content = f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages("src"),
    install_requires=[
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "mlflow>=1.20.0",
    ],
    entry_points={{
        "console_scripts": [
            "train-model = src.models.train:main",
        ],
    }},
)
'''

        with open(project_dir / "setup.py", "w") as f:
            f.write(setup_content)

        # Create .gitignore
        gitignore_content = '''# ML specific
*.model
*.pkl
*.joblib
*.h5
*.pt
*.pth
*.onnx
*.pb
*.tflite
*.safetensors

# Data
*.csv
*.json
*.xml
*.parquet
*.hdf5
*.npz

# Jupyter notebooks
.ipynb_checkpoints/
*.ipynb

# Environment
.venv/
venv/
env/
ENV/

# OS
.DS_Store
Thumbs.db

# MLflow
mlruns/
mlartifacts/

# Model outputs
weights/
checkpoints/

# Pytest
.pytest_cache/
.coverage
htmlcov/
'''

        with open(project_dir / ".gitignore", "w") as f:
            f.write(gitignore_content)

        # Create example training script
        train_script = '''"""
Example training script
"""
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

def load_data():
    """Load your data here"""
    # Example - replace with your actual data loading logic
    print("Loading data...")
    # For example: data = pd.read_csv("data/processed/train.csv")
    # Returning dummy data for the example
    import numpy as np
    X = np.random.rand(100, 4)
    y = np.random.randint(0, 2, 100)
    return X, y

def train_model(X, y):
    """Train the ML model"""
    print("Training model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model accuracy: {accuracy:.4f}")

    return model

def save_model(model, filepath):
    """Save the trained model"""
    joblib.dump(model, filepath)
    print(f"Model saved to {filepath}")

def main():
    X, y = load_data()
    model = train_model(X, y)
    save_model(model, "models/trained_model.pkl")

if __name__ == "__main__":
    main()
'''

        with open(project_dir / "src" / "models" / "train.py", "w") as f:
            f.write(train_script)

        print(f"\n✓ ML project '{project_name}' created successfully!")
        print(f"Directory structure:")
        print(f"├── data/")
        print(f"│   ├── raw/")
        print(f"│   ├── processed/")
        print(f"│   └── external/")
        print(f"├── notebooks/")
        print(f"├── src/")
        print(f"│   ├── data/")
        print(f"│   ├── features/")
        print(f"│   ├── models/")
        print(f"│   └── visualization/")
        print(f"├── models/")
        print(f"├── reports/")
        print(f"├── tests/")
        print(f"├── requirements.txt")
        print(f"├── setup.py")
        print(f"└── .gitignore")

        input("\nPress Enter to continue...")

    def manage_ml_experiments(self) -> None:
        """Help manage machine learning experiments"""
        print("\n" + "="*70)
        print("ML EXPERIMENT TRACKING & MANAGEMENT")
        print("="*70)

        print("\nThis tool helps track ML experiments using tools like MLflow or Weights & Biases.")

        print("\nAvailable experiment tracking tools:")
        print("  1. MLflow")
        print("  2. Weights & Biases (wandb)")
        print("  3. TensorBoard")
        print("  4. Neptune")

        try:
            choice = input("\nEnter choice (1-4) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_mlflow()
            elif choice == "2":
                self._setup_wandb()
            elif choice == "3":
                self._setup_tensorboard()
            elif choice == "4":
                self._setup_neptune()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_mlflow(self) -> None:
        """Setup MLflow tracking"""
        print("\nSetting up MLflow tracking...")

        try:
            import mlflow
            print("✓ MLflow is installed")
        except ImportError:
            install = input("MLflow is not installed. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "mlflow"], check=True)
                    print("✓ MLflow installed successfully")
                    import mlflow
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install MLflow")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without MLflow.")
                input("\nPress Enter to continue...")
                return

        print("\nMLflow tracking server setup:")
        print("  - Local: mlflow server --backend-store-uri ./mlruns --default-artifact-root ./mlartifacts")
        print("  - Remote: mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db")

        print("\nExample Python code for tracking:")
        print("# Start run")
        print("with mlflow.start_run():")
        print("    # Log parameters")
        print("    mlflow.log_param('learning_rate', 0.01)")
        print("    # Log metrics")
        print("    mlflow.log_metric('accuracy', 0.95)")
        print("    # Log artifacts")
        print("    mlflow.log_artifact('model.pkl')")

        print("\nTo view the UI:")
        print("  mlflow ui --backend-store-uri ./mlruns")
        print("Then visit http://localhost:5000")

    def _setup_wandb(self) -> None:
        """Setup Weights & Biases tracking"""
        print("\nSetting up Weights & Biases tracking...")

        try:
            import wandb
            print("✓ wandb is installed")
        except ImportError:
            install = input("wandb is not installed. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "wandb"], check=True)
                    print("✓ wandb installed successfully")
                    import wandb
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install wandb")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without wandb.")
                input("\nPress Enter to continue...")
                return

        print("\nTo initialize wandb:")
        print("  wandb login")
        print("  Then follow the prompts to authenticate")

        print("\nExample Python code for tracking:")
        print("import wandb")
        print("wandb.init(project='my-project', config={'lr': 0.01})")
        print("# Log metrics during training")
        print("wandb.log({'accuracy': 0.95})")
        print("wandb.finish()")

    def _setup_tensorboard(self) -> None:
        """Setup TensorBoard tracking"""
        print("\nSetting up TensorBoard tracking...")

        try:
            import torch
            print("✓ PyTorch is available (for tensorboard with PyTorch)")
        except ImportError:
            print("ℹ PyTorch not found (install for PyTorch integration)")

        try:
            import tensorflow as tf
            print("✓ TensorFlow is available (for tensorboard with TensorFlow)")
        except ImportError:
            print("ℹ TensorFlow not found (install for TensorFlow integration)")

        try:
            from torch.utils.tensorboard import SummaryWriter
            print("✓ TensorBoard is available")
        except ImportError:
            install = input("TensorBoard is not available. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "tensorboard"], check=True)
                    print("✓ TensorBoard installed successfully")
                    from torch.utils.tensorboard import SummaryWriter
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install TensorBoard")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without TensorBoard.")
                input("\nPress Enter to continue...")
                return

        print("\nTo use TensorBoard:")
        print("  tensorboard --logdir=runs")
        print("Then visit http://localhost:6006")

        print("\nExample Python code for logging:")
        print("from torch.utils.tensorboard import SummaryWriter")
        print("writer = SummaryWriter('runs/exp1')")
        print("writer.add_scalar('accuracy', 0.95, global_step=1)")
        print("writer.close()")

    def _setup_neptune(self) -> None:
        """Setup Neptune tracking"""
        print("\nSetting up Neptune tracking...")

        try:
            import neptune
            print("✓ Neptune is installed")
        except ImportError:
            install = input("Neptune is not installed. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "neptune"], check=True)
                    print("✓ Neptune installed successfully")
                    import neptune
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Neptune")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without Neptune.")
                input("\nPress Enter to continue...")
                return

        print("\nTo initialize Neptune:")
        print("  1. Create an account at neptune.ai")
        print("  2. Get your API token from the dashboard")
        print("  3. Initialize: neptune.init_run(project='workspace-name/project-name')")

        print("\nExample Python code for tracking:")
        print("import neptune")
        print("run = neptune.init_run(project='workspace-name/project-name',")
        print("              api_token='YOUR_API_TOKEN')")
        print("run['parameters'] = {'lr': 0.01}")
        print("run['accuracy'] = 0.95")
        print("run.stop()")

    def create_data_pipeline(self) -> None:
        """Help create data preprocessing and pipeline tools"""
        print("\n" + "="*70)
        print("DATA PIPELINE & PREPROCESSING TOOLS")
        print("="*70)

        print("\nThis tool helps create data pipelines and preprocessing scripts.")

        print("\nCommon data pipeline frameworks:")
        print("  1. Pandas (for simple pipelines)")
        print("  2. Dask (for larger-than-memory datasets)")
        print("  3. Apache Airflow (for complex workflows)")
        print("  4. Kedro (for standardized ML pipelines)")
        print("  5. Prefect (for workflow management)")

        try:
            choice = input("\nEnter choice (1-5) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_pandas_pipeline()
            elif choice == "2":
                self._setup_dask_pipeline()
            elif choice == "3":
                self._setup_airflow_pipeline()
            elif choice == "4":
                self._setup_kedro_pipeline()
            elif choice == "5":
                self._setup_prefect_pipeline()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_pandas_pipeline(self) -> None:
        """Setup pandas-based data pipeline"""
        print("\nSetting up pandas-based data pipeline...")

        # Create example pipeline script
        pipeline_script = '''"""
Example data preprocessing pipeline using pandas
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

class DataPipeline:
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoders = {}

    def load_data(self, filepath):
        """Load data from file"""
        print(f"Loading data from {filepath}")
        return pd.read_csv(filepath)

    def clean_data(self, df):
        """Clean the data"""
        print("Cleaning data...")
        # Remove duplicates
        df = df.drop_duplicates()

        # Handle missing values
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col].fillna(df[col].mean(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)

        return df

    def encode_categorical(self, df, categorical_columns):
        """Encode categorical variables"""
        print(f"Encoding categorical columns: {categorical_columns}")
        for col in categorical_columns:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                df[col] = self.encoders[col].fit_transform(df[col].astype(str))
            else:
                df[col] = self.encoders[col].transform(df[col].astype(str))

        return df

    def scale_features(self, df, feature_columns, fit=True):
        """Scale numerical features"""
        print("Scaling features...")
        if fit:
            scaled_features = self.scaler.fit_transform(df[feature_columns])
        else:
            scaled_features = self.scaler.transform(df[feature_columns])

        df[feature_columns] = scaled_features
        return df

    def split_data(self, df, target_column, test_size=0.2):
        """Split data into train and test sets"""
        print("Splitting data...")
        X = df.drop(columns=[target_column])
        y = df[target_column]
        return train_test_split(X, y, test_size=test_size, random_state=42)

    def run_pipeline(self, input_path, target_column, categorical_columns, feature_columns):
        """Run the entire pipeline"""
        df = self.load_data(input_path)
        df = self.clean_data(df)
        df = self.encode_categorical(df, categorical_columns)
        df = self.scale_features(df, feature_columns)

        X_train, X_test, y_train, y_test = self.split_data(df, target_column)

        return X_train, X_test, y_train, y_test

# Example usage
if __name__ == "__main__":
    pipeline = DataPipeline()

    # Example - replace with your actual column names
    # X_train, X_test, y_train, y_test = pipeline.run_pipeline(
    #     "data/processed/train.csv",
    #     target_column="target",
    #     categorical_columns=["category"],
    #     feature_columns=["feature1", "feature2", "feature3"]
    # )
'''

        with open("data_pipeline.py", "w") as f:
            f.write(pipeline_script)

        print("✓ Created 'data_pipeline.py' example pipeline")
        print("\nTo use the pipeline:")
        print("  1. Modify the example with your column names")
        print("  2. Update the input file path")
        print("  3. Run: python data_pipeline.py")

    def _setup_dask_pipeline(self) -> None:
        """Setup Dask-based data pipeline"""
        print("\nSetting up Dask-based data pipeline...")

        # Check if Dask is available
        try:
            import dask
            print("✓ Dask is installed")
        except ImportError:
            install = input("Dask is not installed. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "dask[dataframe]"], check=True)
                    print("✓ Dask installed successfully")
                    import dask
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Dask")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without Dask.")
                input("\nPress Enter to continue...")
                return

        print("\nDask allows processing datasets larger than memory.")
        print("Example Dask pipeline:")
        print("  import dask.dataframe as dd")
        print("  df = dd.read_csv('large_dataset.csv')")
        print("  df_cleaned = df.dropna().compute()  # Clean and bring to memory")

        print("\nFor parallel processing, Dask automatically distributes operations.")

    def _setup_airflow_pipeline(self) -> None:
        """Setup Apache Airflow pipeline"""
        print("\nSetting up Apache Airflow pipeline...")

        print("Apache Airflow is a platform to programmatically author, schedule, and monitor workflows.")
        print("\nTo install Airflow:")
        print("  pip install apache-airflow")
        print("  airflow db init  # Initialize the database")
        print("  airflow webserver --daemon  # Start the web server")
        print("  airflow scheduler --daemon  # Start the scheduler")

        print("\nAirflow DAGs (Directed Acyclic Graphs) define your workflows.")
        print("Visit http://localhost:8080 to access the Airflow UI.")

    def _setup_kedro_pipeline(self) -> None:
        """Setup Kedro pipeline"""
        print("\nSetting up Kedro pipeline...")

        # Check if Kedro is available
        try:
            result = subprocess.run(['kedro', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Kedro is installed")
            else:
                print("⚠ Kedro is not installed properly")
        except FileNotFoundError:
            print("⚠ Kedro is not installed")

        install = input("Install Kedro? (y/n): ").lower()
        if install == 'y':
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "kedro"], check=True)
                print("✓ Kedro installed successfully")
            except subprocess.CalledProcessError:
                print("⚠ Failed to install Kedro")

        print("\nTo create a new Kedro project:")
        print("  kedro new")
        print("\nTo run a Kedro project:")
        print("  kedro run")

        print("\nKedro provides a standardized structure for ML pipelines.")
        print("It includes built-in support for experiment tracking and data catalog management.")

    def _setup_prefect_pipeline(self) -> None:
        """Setup Prefect pipeline"""
        print("\nSetting up Prefect pipeline...")

        # Check if Prefect is available
        try:
            result = subprocess.run(['prefect', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Prefect is installed")
            else:
                print("⚠ Prefect is not installed properly")
        except FileNotFoundError:
            print("⚠ Prefect is not installed")

        install = input("Install Prefect? (y/n): ").lower()
        if install == 'y':
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "prefect"], check=True)
                print("✓ Prefect installed successfully")
            except subprocess.CalledProcessError:
                print("⚠ Failed to install Prefect")

        print("\nExample Prefect flow:")
        print("  from prefect import flow, task")
        print("  @task")
        print("  def extract_data():")
        print("      return [1, 2, 3]")
        print("  @flow")
        print("  def my_pipeline():")
        print("      data = extract_data()")
        print("      return data")
        print("  my_pipeline()")

    def deploy_ml_model(self) -> None:
        """Help deploy machine learning models"""
        print("\n" + "="*70)
        print("ML MODEL DEPLOYMENT TOOLS")
        print("="*70)

        print("\nThis tool helps deploy ML models to various platforms.")

        print("\nDeployment options:")
        print("  1. Flask/FastAPI (simple REST API)")
        print("  2. Docker + Kubernetes")
        print("  3. AWS SageMaker")
        print("  4. Google Cloud AI Platform")
        print("  5. Microsoft Azure Machine Learning")
        print("  6. Hugging Face Spaces")

        try:
            choice = input("\nEnter choice (1-6) or press Enter to cancel: ").strip()

            if choice == "1":
                self._deploy_simple_api()
            elif choice == "2":
                self._deploy_docker_k8s()
            elif choice == "3":
                self._deploy_aws_sagemaker()
            elif choice == "4":
                self._deploy_gcp_ai_platform()
            elif choice == "5":
                self._deploy_azure_ml()
            elif choice == "6":
                self._deploy_huggingface_spaces()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _deploy_simple_api(self) -> None:
        """Deploy model as simple Flask/FastAPI API"""
        print("\nDeploying model as simple API...")

        print("\nCreating example FastAPI service...")

        api_content = '''from fastapi import FastAPI
import joblib
import pandas as pd
import numpy as np

# Load pre-trained model
model = joblib.load('model.pkl')

app = FastAPI(
    title="ML Model API",
    description="API for machine learning model prediction",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/predict")
def predict(input_data: dict):
    """
    Make a prediction using the ML model
    """
    # Convert input to the format expected by the model
    features = [input_data[key] for key in sorted(input_data.keys())]
    features_array = np.array(features).reshape(1, -1)

    # Make prediction
    prediction = model.predict(features_array)
    probability = model.predict_proba(features_array) if hasattr(model, 'predict_proba') else None

    result = {
        "prediction": prediction.tolist()[0],
        "probabilities": probability.tolist()[0] if probability is not None else None
    }

    return result

# To run: uvicorn main:app --reload
'''

        with open("model_api.py", "w") as f:
            f.write(api_content)

        print("✓ Created 'model_api.py' example service")

        print("\nTo run the API:")
        print("  1. Save your trained model as 'model.pkl'")
        print("  2. Install dependencies: pip install fastapi uvicorn scikit-learn")
        print("  3. Run: uvicorn model_api:app --reload")
        print("  4. Visit http://localhost:8000/docs for API documentation")

    def _deploy_docker_k8s(self) -> None:
        """Deploy model using Docker and Kubernetes"""
        print("\nDeploying model using Docker and Kubernetes...")

        print("\nCreating example Dockerfile...")

        dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "model_api:app", "--host", "0.0.0.0", "--port", "8000"]
'''

        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)

        requirements_content = '''fastapi==0.100.0
uvicorn==0.22.0
scikit-learn==1.3.0
pandas==1.5.0
joblib==1.2.0
'''

        with open("requirements.txt", "w") as f:
            f.write(requirements_content)

        print("✓ Created 'Dockerfile' and 'requirements.txt'")

        print("\nTo build and run:")
        print("  1. Build: docker build -t ml-model-api .")
        print("  2. Run: docker run -p 8000:8000 ml-model-api")

        print("\nFor Kubernetes deployment, you'll need:")
        print("  - A Kubernetes cluster (Minikube, GKE, EKS, etc.)")
        print("  - kubectl installed and configured")
        print("  - A Kubernetes deployment YAML file")

    def _deploy_aws_sagemaker(self) -> None:
        """Deploy model to AWS SageMaker"""
        print("\nDeploying model to AWS SageMaker...")

        print("\nAWS SageMaker provides managed ML model deployment.")
        print("Steps to deploy:")
        print("  1. Prepare your model artifact (trained model files)")
        print("  2. Create a model configuration using the SageMaker Python SDK")
        print("  3. Deploy the model to a SageMaker endpoint")

        print("\nExample deployment code:")
        print("  import sagemaker")
        print("  from sagemaker.sklearn.model import SKLearnModel")
        print("  sklearn_model = SKLearnModel(model_data='s3://bucket/model.tar.gz',")
        print("                            role='arn:aws:iam::account:role/MySageMakerRole',")
        print("                            entry_point='inference.py')")
        print("  predictor = sklearn_model.deploy(initial_instance_count=1, instance_type='ml.m5.large')")

    def _deploy_gcp_ai_platform(self) -> None:
        """Deploy model to Google Cloud AI Platform"""
        print("\nDeploying model to Google Cloud AI Platform...")

        print("\nGoogle Cloud AI Platform provides managed ML model deployment.")
        print("Steps to deploy:")
        print("  1. Prepare your model in the required format")
        print("  2. Upload model to Google Cloud Storage")
        print("  3. Create and deploy model using gcloud CLI or Python SDK")

        print("\nExample deployment command:")
        print("  gcloud ai-platform models create my-model --regions=us-central1")
        print("  gcloud ai-platform versions create v1 --model=my-model --origin=gs://my-bucket/my-model/")

    def _deploy_azure_ml(self) -> None:
        """Deploy model to Microsoft Azure Machine Learning"""
        print("\nDeploying model to Microsoft Azure Machine Learning...")

        print("\nAzure ML provides managed ML model deployment.")
        print("Steps to deploy:")
        print("  1. Register your model in Azure Model Registry")
        print("  2. Create an Azure Container Instance or Azure Kubernetes Service")
        print("  3. Deploy the model using Azure ML SDK")

        print("\nExample deployment code:")
        print("  from azureml.core import Workspace, Model")
        print("  from azureml.core.webservice import AciWebservice")
        print("  from azureml.core.model import InferenceConfig")
        print("  # Deploy model to ACI")
        print("  deployment_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=1)")
        print("  service = Model.deploy(ws, 'my-service', [model], inference_config, deployment_config)")

    def _deploy_huggingface_spaces(self) -> None:
        """Deploy model to Hugging Face Spaces"""
        print("\nDeploying model to Hugging Face Spaces...")

        print("\nHugging Face Spaces provides free, shareable apps for ML models.")
        print("Steps to deploy:")
        print("  1. Create a Hugging Face account")
        print("  2. Create a Space with your model and code")
        print("  3. Use the Gradio or Streamlit interfaces for UI")

        print("\nExample Gradio interface:")
        print("  import gradio as gr")
        print("  import joblib")
        print("  model = joblib.load('model.pkl')")
        print("  def predict(input):")
        print("      # Process input and return prediction")
        print("      return model.predict([input])[0]")
        print("  gr.Interface(predict, inputs='text', outputs='label').launch()")
class AIMLMenu(Menu):
    """Menu for AI/ML tools"""

    def __init__(self):
        self.ai_ml = AIMLTools()
        super().__init__("AI & Machine Learning Tools")

    def setup_items(self) -> None:
        """Setup menu items for AI/ML tools"""
        self.items = [
            MenuItem("Setup ML Project", self.ai_ml.setup_ml_project),
            MenuItem("Manage ML Experiments", self.ai_ml.manage_ml_experiments),
            MenuItem("Create Data Pipeline", self.ai_ml.create_data_pipeline),
            MenuItem("Deploy ML Model", self.ai_ml.deploy_ml_model),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]