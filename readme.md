# Urban Heat Intelligence System

## Overview

The **Urban Heat Intelligence System** is a Streamlit-based application designed to analyze, visualize, and mitigate urban heat patterns. It integrates machine learning, geospatial insights, and live weather data to provide actionable intelligence for urban planning and environmental monitoring.

---

## Features

* **Zone Analysis**: Evaluate heat distribution across different urban zones
* **Live Map Visualization**: Real-time geospatial heat mapping
* **Mitigation Planning**: Suggest strategies to reduce urban heat impact
* **Ranking System**: Rank zones based on heat severity
* **Planning Module**: Assist in long-term urban cooling strategies
* **Historical Insights**: Track and analyze past heat trends
* **ML Model Integration**: Predictive modeling using a trained weather model

---

## Project Structure

```
.
├── .streamlit/
│   └── secrets.toml        # API keys and secrets
├── notebooks/              # Jupyter notebook for training
├── utils/
│   ├── util.py
│   ├── zone_analysis.py
│   ├── livemap.py
│   ├── mitigation.py
│   ├── ranking.py
│   ├── planning.py
│   └── history.py
├── db.py                   # Database initialization and management
├── app.py     # Main Streamlit application
├── weather_model_updated.pkl
├── urban_heat.db
├── requirements.txt
├── runtime.txt
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mohammedavez125/Urban_Heat_Mitigation_System
cd Urban_Heat_Mitigation_System
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## API Key Setup (OpenWeather)

This project uses the OpenWeather API for real-time weather data.

### Step 1: Generate API Key

1. Go to: https://home.openweathermap.org/
2. Sign up / log in
3. Navigate to **API Keys**
4. Copy your API key

---

### Step 2: Store API Key

Create the file:

```
.streamlit/secrets.toml
```

Add:

```toml
API_KEY = "your_api_key_here"
```

---

## Optional: Windows Automation for API Key Setup

You can automate the creation of the secrets file using a Windows script.

### Option 1: Batch Script

Create a file named `setup_secrets.bat`:

```bat
@echo off
set /p API_KEY=Enter your OpenWeather API Key: 

if not exist .streamlit (
    mkdir .streamlit
)

echo API_KEY = "%API_KEY%" > .streamlit\secrets.toml

echo Secrets file created successfully.
pause
```

Run:

```bash
setup_secrets.bat
```

---

### Option 2: PowerShell Script

Create `setup_secrets.ps1`:

```powershell
$apiKey = Read-Host "Enter your OpenWeather API Key"

if (!(Test-Path ".streamlit")) {
    New-Item -ItemType Directory -Path ".streamlit"
}

"API_KEY = `"$apiKey`"" | Out-File ".streamlit/secrets.toml"

Write-Host "Secrets file created successfully."
```

Run:

```powershell
powershell -ExecutionPolicy Bypass -File setup_secrets.ps1
```

---

## Running the Application

```bash
streamlit run app.py
```

---

## Model

* File: `weather_model_updated.pkl`
* Loaded using `joblib`
* Used for predictive heat analysis

---

## Database

* SQLite database: `urban_heat.db`
* Initialized automatically via:

```python
from db import *
init_db()
```

---

## Dependencies

Key libraries include:

* streamlit
* requests
* pandas
* folium
* streamlit-folium
* plotly
* joblib
* streamlit-option-menu
* scikit-learn==1.6.1

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

## Notes

* Ensure your API key is valid and active before running the app
* The `.streamlit/secrets.toml` file should not be committed to version control
* Add `.streamlit/secrets.toml` to `.gitignore`

---

## Future Improvements

* Deployment on cloud platforms (Streamlit Cloud / AWS / Azure)
* Integration with satellite heat data
* Advanced ML models for higher prediction accuracy
* User authentication and dashboards

---

## License

Specify your license here (e.g., MIT License)
