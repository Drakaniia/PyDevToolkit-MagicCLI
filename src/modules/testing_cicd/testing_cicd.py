import sys
import subprocess
import os
from pathlib import Path
from typing import List, Optional
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator

"""
Testing & CI/CD Module
Handles test execution, coverage analysis, and CI/CD pipeline integration
"""


class TestingCICDTools:
    """Handles testing and CI/CD integration tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def run_unit_tests(self) -> None:
        """Run unit tests with pytest"""
        print("\n" + "=" * 70)
        print("RUNNING UNIT TESTS")
        print("=" * 70)

        try:
            # Run unit tests only with pytest
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/unit/", "-v"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("\n✓ All unit tests passed!")
            else:
                print("\nUnit tests failed:\n")
                print(result.stdout)
                if result.stderr:
                    print(f"\nErrors: {result.stderr}")

        except FileNotFoundError:
            print("\n⚠ Pytest is not installed or no unit tests found")
        except Exception as e:
            print(f"\n⚠ Error running unit tests: {e}")

        input("\nPress Enter to continue...")

    def run_integration_tests(self) -> None:
        """Run integration tests with pytest"""
        print("\n" + "=" * 70)
        print("RUNNING INTEGRATION TESTS")
        print("=" * 70)

        try:
            # Run integration tests only with pytest
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/integration/", "-v"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("\n✓ All integration tests passed!")
            else:
                print("\nIntegration tests failed:\n")
                print(result.stdout)
                if result.stderr:
                    print(f"\nErrors: {result.stderr}")

        except FileNotFoundError:
            print("\n⚠ Pytest is not installed or no integration tests found")
        except Exception as e:
            print(f"\n⚠ Error running integration tests: {e}")

        input("\nPress Enter to continue...")

    def run_all_tests(self) -> None:
        """Run all tests with coverage"""
        print("\n" + "=" * 70)
        print("RUNNING ALL TESTS WITH COVERAGE")
        print("=" * 70)

        try:
            # Run all tests with coverage
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/",
                "-v", "--cov=src", "--cov-report=term-missing"
            ], capture_output=True, text=True)

            print("\nTest Results:\n")
            print(result.stdout)
            if result.stderr:
                print(f"\nErrors: {result.stderr}")

        except Exception as e:
            print(f"\n⚠ Error running tests: {e}")

        input("\nPress Enter to continue...")

    def run_test_coverage(self) -> None:
        """Generate and display test coverage"""
        print("\n" + "=" * 70)
        print("RUNNING TEST COVERAGE ANALYSIS")
        print("=" * 70)

        try:
            # Run coverage analysis only
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "--cov=src", "--cov-report=term-missing",
                "--cov-report=html:htmlcov", "--cov-report=xml"
            ], capture_output=True, text=True)

            print("\nCoverage Analysis Results:\n")
            print(result.stdout)
            if result.stderr:
                print(f"\nErrors: {result.stderr}")

            print("\nHTML coverage report saved to 'htmlcov/' directory")
            print("XML coverage report saved as 'coverage.xml'")

        except Exception as e:
            print(f"\n⚠ Error running coverage analysis: {e}")

        input("\nPress Enter to continue...")

    def generate_test_report(self) -> None:
        """Generate a comprehensive test report"""
        print("\n" + "=" * 70)
        print("GENERATING COMPREHENSIVE TEST REPORT")
        print("=" * 70)

        try:
            # Run tests with multiple output formats
            print("Running tests and generating reports...")
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--junit-xml=test-results.xml",
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml"
            ], capture_output=True, text=True)

            print("\nTest Results:\n")
            print(result.stdout)

            if result.returncode == 0:
                print("\n✓ Tests completed successfully!")
            else:
                print("\n⚠ Some tests failed")

            if result.stderr:
                print(f"\nErrors: {result.stderr}")

        except Exception as e:
            print(f"\n⚠ Error generating test report: {e}")

        input("\nPress Enter to continue...")

    def run_ci_checks(self) -> None:
        """Run all CI checks (formatting, linting, type checking, tests)"""
        print("\n" + "=" * 70)
        print("RUNNING CI CHECKS (Format, Lint, Type, Test)")
        print("=" * 70)

        print("This would typically run in a CI environment.")
        print("For local execution, this runs a comprehensive check.")

        # We'll call the appropriate functions from other modules
        # This is a simplified version - in a real scenario,
        # we would have access to the functions from other modules
        try:
            # Check formatting
            print("\n1. Checking code formatting...")
            format_result = subprocess.run([
                sys.executable, "-m", "black", "--check", "src/", "tests/"
            ], capture_output=True, text=True)

            if format_result.returncode == 0:
                print("   ✓ Code formatting is correct")
            else:
                print("   ⚠ Code formatting issues found")
                print(format_result.stdout[:500] + "..." if len(
                    format_result.stdout) > 500 else format_result.stdout)

            # Run linting
            print("\n2. Running linting...")
            lint_result = subprocess.run([
                sys.executable, "-m", "flake8", "src/",
                "--max-line-length=88", "--extend-ignore=E203,W503"
            ], capture_output=True, text=True)

            if lint_result.returncode == 0:
                print("   ✓ No linting issues found")
            else:
                print("   ⚠ Linting issues found")
                print(lint_result.stdout[:500] + "..." if len(
                    lint_result.stdout) > 500 else lint_result.stdout)

            # Run type checking
            print("\n3. Running type checking...")
            type_result = subprocess.run([
                sys.executable, "-m", "mypy", "src/"
            ], capture_output=True, text=True)

            if type_result.returncode == 0:
                print("   ✓ Type checking passed")
            else:
                print("   ⚠ Type checking issues found")
                print(type_result.stdout[:500] + "..." if len(
                    type_result.stdout) > 500 else type_result.stdout)

            # Run tests
            print("\n4. Running tests...")
            test_result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "--tb=short"
            ], capture_output=True, text=True)

            if test_result.returncode == 0:
                print("   ✓ All tests passed")
            else:
                print("   ⚠ Some tests failed")
                print(test_result.stdout[:500] + "..." if len(
                    test_result.stdout) > 500 else test_result.stdout)

            print("\nCI Checks completed!")

        except Exception as e:
            print(f"\n⚠ Error running CI checks: {e}")

        input("\nPress Enter to continue...")

    def setup_ci_pipeline(self) -> None:
        """Help set up CI pipeline configuration"""
        print("\n" + "=" * 70)
        print("SETTING UP CI PIPELINE")
        print("=" * 70)

        print("This tool helps you create CI pipeline configuration files.")
        print("\nAvailable CI platforms:")
        print("  1. GitHub Actions")
        print("  2. GitLab CI")
        print("  3. Jenkins")
        print("  4. CircleCI")
        print("  5. Travis CI")

        try:
            choice = input(
                "\nSelect a CI platform (1-5) or press Enter to cancel: ").strip()

            if choice == "1":
                self._create_github_actions_config()
            elif choice == "2":
                self._create_gitlab_ci_config()
            elif choice == "3":
                self._create_jenkins_config()
            elif choice == "4":
                self._create_circleci_config()
            elif choice == "5":
                self._create_travis_config()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _create_github_actions_config(self) -> None:
        """Create GitHub Actions workflow configuration"""
        github_dir = Path(".github/workflows")
        github_dir.mkdir(parents=True, exist_ok=True)

        workflow_content = """name: Python CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev,test]"
    - name: Check formatting
      run: |
        black --check src/ tests/
    - name: Lint with flake8
      run: |
        flake8 src/ tests/
    - name: Type check with mypy
      run: |
        mypy src/
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
"""

        workflow_path = github_dir / "python-app.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)

        print(f"\n✓ GitHub Actions workflow created: {workflow_path}")
        print("Remember to enable GitHub Actions in your repository settings.")

    def _create_gitlab_ci_config(self) -> None:
        """Create GitLab CI configuration"""
        config_content = """stages:
  - test
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

before_script:
  - python -version
  - pip install virtualenv
  - virtualenv venv
  - source venv/bin/activate
  - pip install -e ".[dev,test]"

test:
  stage: test
  script:
    - black --check src/ tests/
    - flake8 src/ tests/
    - mypy src/
    - pytest tests/ -v --cov=src --cov-report=xml
  coverage: '/TOTAL.* (\\d+\\.?\\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  only:
    - branches

deploy:
  stage: deploy
  script:
    - echo "Deployment to be configured"
  only:
    - main
"""

        config_path = Path(".gitlab-ci.yml")
        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"\n✓ GitLab CI configuration created: {config_path}")

    def _create_jenkins_config(self) -> None:
        """Create Jenkins pipeline configuration"""
        config_content = """pipeline {
    agent any

    tools {
        python 'Python3'  // Configure this in Jenkins global tools
    }

    environment {
        PATH = "${workspace}/venv/bin:${PATH}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                sh 'python -m venv venv'
                sh 'source venv/bin/activate && pip install --upgrade pip'
                sh 'source venv/bin/activate && pip install -e ".[dev,test]"'
            }
        }

        stage('Code Quality') {
            parallel {
                stage('Format Check') {
                    steps {
                        sh 'source venv/bin/activate && black --check src/ tests/'
                    }
                }
                stage('Lint') {
                    steps {
                        sh 'source venv/bin/activate && flake8 src/ tests/'
                    }
                }
                stage('Type Check') {
                    steps {
                        sh 'source venv/bin/activate && mypy src/'
                    }
                }
            }
        }

        stage('Test') {
            steps {
                sh 'source venv/bin/activate && pytest tests/ -v --cov=src --cov-report=xml'
            }
            post {
                always {
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')]
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
"""

        config_path = Path("Jenkinsfile")
        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"\n✓ Jenkins pipeline configuration created: {config_path}")

    def _create_circleci_config(self) -> None:
        """Create CircleCI configuration"""
        circle_dir = Path(".circleci")
        circle_dir.mkdir(exist_ok=True)

        config_content = """version: 2.1

orbs:
  python: circleci/python@2.1.1

jobs:
  test:
    parameters:
      python-version:
        type: string
    docker:
      - image: cimg/python:<< parameters.python-version >>
    steps:
      - checkout
      - python/install-packages:
          pip-dependency-file: requirements-dev.txt
          pkg-manager: pip
      - run:
          name: Install project in development mode
          command: pip install -e ".[dev,test]"
      - run:
          name: Check formatting
          command: black --check src/ tests/
      - run:
          name: Lint
          command: flake8 src/ tests/
      - run:
          name: Type check
          command: mypy src/
      - run:
          name: Run tests with coverage
          command: pytest tests/ -v --cov=src --cov-report=xml
      - store_test_results:
          path: test-results
      - store_artifacts:
          path: htmlcov

workflows:
  test:
    jobs:
      - test:
          matrix:
            parameters:
              python-version: ["3.7", "3.8", "3.9", "3.10", "3.11"]
  build-and-deploy:
    jobs:
      - test
"""

        config_path = circle_dir / "config.yml"
        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"\n✓ CircleCI configuration created: {config_path}")

    def _create_travis_config(self) -> None:
        """Create Travis CI configuration"""
        config_content = """language: python
python:
  - "3.7"
  - "3.8"
  - "3.9"
  - "3.10"
  - "3.11"

cache: pip

install:
  - pip install --upgrade pip
  - pip install -e ".[dev,test]"

script:
  - black --check src/ tests/
  - flake8 src/ tests/
  - mypy src/
  - pytest tests/ -v --cov=src

after_success:
  - bash <(curl -s https://codecov.io/bash)

notifications:
  email: false
"""

        config_path = Path(".travis.yml")
        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"\n✓ Travis CI configuration created: {config_path}")


class TestingCICDMenu(Menu):
    """Menu for testing and CI/CD tools"""

    def __init__(self):
        self.testing_cicd = TestingCICDTools()
        super().__init__("Testing & CI/CD Tools")

    def setup_items(self) -> None:
        """Setup menu items for testing and CI/CD tools"""
        self.items = [
            MenuItem("Run Unit Tests", self.testing_cicd.run_unit_tests),
            MenuItem("Run Integration Tests", self.testing_cicd.run_integration_tests),
            MenuItem("Run All Tests with Coverage", self.testing_cicd.run_all_tests),
            MenuItem("Generate Test Coverage Report", self.testing_cicd.run_test_coverage),
            MenuItem("Generate Comprehensive Test Report", self.testing_cicd.generate_test_report),
            MenuItem("Run CI Checks (Local Simulation)", self.testing_cicd.run_ci_checks),
            MenuItem("Setup CI Pipeline Configuration", self.testing_cicd.setup_ci_pipeline),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]
