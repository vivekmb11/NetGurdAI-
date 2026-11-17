# Deep Learning-Based Web Attack Detection & Early Warning System

## Project Objective

A web-based cybersecurity platform designed to analyze website and network traffic flows to identify abnormal, intrusive, or malicious behavior in real time. The platform integrates Deep Learning architectures (1D-CNN, LSTM/GRU, CNN-LSTM, and Autoencoder) for high-accuracy multi-class attack classification and unsupervised zero-day anomaly detection.

## Technology Stack

- **Python** 3.10+
- **Flask** - Web backend and REST API
- **TensorFlow/Keras** - Deep Learning model implementations
- **NumPy (<2.0), Pandas, Polars, PyArrow** - High-performance data processing and serialization
- **Scikit-learn** - Data scaling, stratified splitting, and evaluation metrics
- **SQLite / SQLAlchemy** - Threat logging and system metadata database
- **HTML5, CSS3, JavaScript** - Analyst dashboard interface

---

## Dataset: CIC-IDS2017

- **Dataset**: Canadian Institute for Cybersecurity Intrusion Detection System 2017 (CIC-IDS2017)
- **Dataset Type**: Labeled bidirectional network-flow traffic data generated via CICFlowMeter from 5 days of realistic enterprise traffic.
- **Input**: 68 selected numerical network-flow features capturing statistical flow duration, packet distributions, inter-arrival times (IAT), byte/packet transmission rates, TCP flags, and subflow metrics.
- **Original Captures**: 8 CSV files totaling 2,830,743 raw flow records across 79 raw attributes.

### Class Labels & Taxonomy

The dataset features 15 raw traffic labels mapped into 8 project categories:

| Class ID | Project Category | Raw Labels Included | Raw Count | Cleaned Count | Share (%) |
|:---:|:---|:---|:---:|:---:|:---:|
| **0** | **BENIGN** | `BENIGN` | 2,273,097 | 2,094,950 | 83.11% |
| **1** | **DoS** | `DoS Hulk`, `DoS GoldenEye`, `DoS slowloris`, `DoS Slowhttptest`, `Heartbleed` | 252,672 | 193,756 | 7.69% |
| **2** | **DDoS** | `DDoS` (LOIC traffic) | 128,027 | 128,014 | 5.08% |
| **3** | **PortScan** | `PortScan` | 158,930 | 90,694 | 3.60% |
| **4** | **BruteForce** | `FTP-Patator`, `SSH-Patator` | 13,835 | 9,150 | 0.36% |
| **5** | **Botnet** | `Bot` (Ares botnet) | 1,966 | 1,948 | 0.08% |
| **6** | **WebAttack** | `Web Attack - Brute Force`, `Web Attack - XSS`, `Web Attack - Sql Injection` | 2,180 | 2,143 | 0.09% |
| **7** | **Infiltration** | `Infiltration` | 36 | 36 | 0.001% |
| — | **Total** | *15 original attack types* | **2,830,743** | **2,520,691** | **100.0%** |

---

## Preprocessing Pipeline

The end-to-end preprocessing pipeline follows a strict, leakage-free sequence:

```
Raw CIC-IDS2017 CSV Captures (8 files, 2,830,743 rows)
                    │
                    ▼
           1. Data Inspection
      (Encoding normalization, column trim)
                    │
                    ▼
           2. Data Cleaning
      (Deduplication: -308,381 duplicate rows)
      (Invalid / Inf / NaN removal: -1,671 rows)
      (Cleaned total: 2,520,691 rows)
                    │
                    ▼
        3. Feature Selection
      (Selected 68 numerical flow features)
      (Removed 11 columns: Target Label, Destination Port identifier,
       Fwd Header Length.1 duplicate, and 8 zero-variance constant features)
                    │
                    ▼
   4. Stratified Train / Val / Test Split
      - 70% Training:   1,764,483 samples
      - 15% Validation:   378,104 samples
      - 15% Testing:      378,104 samples
                    │
                    ▼
      5. Feature Scaling (Zero Leakage)
      (StandardScaler fitted STRICTLY on X_train only)
      (Validation and Test sets transformed using X_train statistics)
                    │
                    ▼
     6. Model-Ready Dataset Serialization
      - X_train.npy, X_val.npy, X_test.npy (float32)
      - y_train.npy, y_val.npy, y_test.npy (int64)
      - X_train_normal.npy (1,466,464 BENIGN flows for Autoencoder)
      - X_val_normal.npy (314,243 BENIGN flows for Autoencoder)
      - models/scaler.pkl (Fitted StandardScaler)
      - data/processed/class_mapping.json & feature_names.json
      - data/processed/class_weights.json (Balanced class weights)
```

---

## Deep Learning Input Shapes

| Architecture | Expected Input Shape | Processing Strategy |
|:---|:---:|:---|
| **Dense / MLP Baseline** | `(batch_size, 68)` | Direct numerical network-flow feature vector |
| **1D CNN** | `(batch_size, 68, 1)` | 1D spatial convolution over correlated flow statistics |
| **LSTM / GRU** | `(batch_size, 1, 68)` | Sequential recurrent modeling across flow time steps |
| **CNN-LSTM** | `(batch_size, T, 68)` | Temporal windowing across sliding consecutive flows |
| **Autoencoder** | `(batch_size, 68)` | Unsupervised reconstruction of normal BENIGN flows |

---

## Execution Guide

### 1. Run Data Cleaning
```bash
python preprocessing/clean_data.py --raw_dir data/raw --output_dir data/processed --format parquet
```

### 2. Run Preprocessing & Splitting Pipeline
```bash
python preprocessing/preprocess.py --cleaned_data data/processed/cleaned_data.parquet --seed 42
```

### 3. Run Validation Tests
```bash
pytest tests/test_preprocessing.py -v
```

### 4. Run Flask Application
```bash
python app.py
```
The application dashboard is available at `http://127.0.0.1:5000`.

---

## Project Structure

```
Web Attack Detection & Early Warning System/
├── app.py                     # Flask application entry point
├── config.py                  # Environment and application configuration
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
├── data/
│   ├── raw/                   # 8 official CIC-IDS2017 raw CSV files (untouched)
│   ├── processed/             # Cleaned Parquet, NumPy arrays (.npy), JSON mappings
│   └── test/                  # Test data samples
├── database/                  # SQLite models and database connection
├── models/
│   └── scaler.pkl             # Fitted StandardScaler (fitted on X_train only)
├── notebooks/
│   ├── dataset_analysis.ipynb # Comprehensive EDA notebook with rendered figures
│   └── plots/                 # Saved visualization PNG artifacts
├── preprocessing/
│   ├── clean_data.py          # Data cleaning pipeline CLI
│   └── preprocess.py          # Feature selection, encoding, scaling, splitting CLI
├── routes/                    # API and view routes
├── services/                  # Business logic and detection service interface
├── templates/                 # HTML templates
├── static/                    # CSS, JavaScript, and UI assets
└── tests/
    └── test_preprocessing.py  # 9 automated data integrity & anti-leakage tests
```

## License

This project is developed for educational and academic research purposes.
