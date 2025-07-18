# Utility Scripts

This folder contains utility scripts for development, testing, and monitoring.

## 📁 Scripts Overview

### `demo_improvements.py`
**Purpose**: Demo script for testing improvements and new features
- Used for development and testing
- Contains sample data and test scenarios
- Run with: `python scripts/demo_improvements.py`

### `monitor.py`
**Purpose**: External monitoring script for production reliability
- Keeps the Render.com service active
- Can run on separate service (Raspberry Pi, VPS, cloud function)
- Run with: `python scripts/monitor.py`

### `run_tests.py`
**Purpose**: Test runner with additional configuration
- Alternative to running `pytest` directly
- Includes coverage reporting and custom test settings
- Run with: `python scripts/run_tests.py`

## 🚀 Usage

```bash
# Run demo improvements
python scripts/demo_improvements.py

# Start external monitoring
python scripts/monitor.py

# Run tests with custom settings
python scripts/run_tests.py
```

## 📋 Requirements

All scripts require the same dependencies as the main application:
- Python 3.11+
- Dependencies listed in `requirements.txt`
- Proper environment variables set

## 🔧 Configuration

Some scripts may require additional configuration:
- `monitor.py`: Set the target URL in the script
- `demo_improvements.py`: Modify sample data as needed
- `run_tests.py`: Adjust test settings in the script 