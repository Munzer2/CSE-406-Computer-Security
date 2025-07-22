# Offline Labs

This repository contains two standalone offline lab assignments:

1. **Lab 1: Cryptography Implementation (Offline1)**  
2. **Lab 2: Website Fingerprinting Pipeline (Offline2)**  

---

## Lab 1: Cryptography Implementation (Offline1)

Implement core cryptographic primitives and a secure client–server exchange.

**Directory:** `Offline1/` 

- **2005018_task1.py**  
  - AES key schedule (key expansion) for 128/192/256-bit keys  
  - PKCS#7 padding/unpadding  
  - Byte ↔ Word conversions, SubWord, RotWord, MixColumns, AddRoundKey helper functions.
- **2005018_task2.py**  
  - Elliptic curve setup over prime fields  
  - Modular inverse, Tonelli–Shanks square root  
  - Point addition, doubling, and scalar multiplication  
- **2005018_task3_ALICE.py** & **2005018_task3_BOB.py**  
  - Socket-based ECDH key exchange (Alice ↔ Bob)  
  - Derive shared secret → SHA-256 → AES-CBC encrypt/decrypt a test message  
- **2005018_utils.py**  
  - Shared S-boxes, inverse S-boxes, Mixers, Rcon constants, BitVector utilities  

---

## Lab 2: Website Fingerprinting Pipeline (Offline2)

Starter code for collecting, storing, post-processing, and classifying network timing traces.

**Directory:** `Offline2/starter_code/template/` 

- **app.py**  
  - Flask server skeleton  
  - Endpoints:  
    - `/collect_trace` (POST) – receive JSON traces, generate heatmaps  
    - `/api/clear_results` (POST) – reset stored traces/heatmaps  
- **collect.py**  
  - Selenium-based trace collector  
  - Automates opening fingerprinting page, interacting with target sites, retrieving results  
- **database.py**  
  - SQLAlchemy models: `Fingerprint`, `CollectionStats`  
  - Methods to init DB, save traces, query counts, export JSON  
- **PostProcess.py**  
  - Re-index dataset entries  
  - Write out corrected JSON for training  
- **train.py**  
  - PyTorch pipeline with two models:  
    - `FingerprintClassifier` (simple CNN)  
    - `ComplexFingerprintClassifier` (deeper CNN + batch norm)  
  - Training loop, evaluation scaffold, classification report  
- **static/index.html**  
  - Pico CSS + Alpine.js UI  
  - Buttons for “Collect Trace”, “Download Traces”, “Clear Results”  
  - Table for latency results and heatmap gallery  

---

## Setup & Usage

> **Note:** We recommend creating a Python virtual environment for Lab 1 to isolate dependencies.

1. **Lab 1 (Cryptography)**  
   ```bash
   cd Offline1
   # Create & activate a venv
   python3 -m venv venv
   source venv/bin/activate        # Linux/macOS
   # OR on Windows:
   # .\venv\Scripts\activate

   # Install core dependencies
   pip install sympy bitvector

   # Run the AES & ECC tasks:
   python3 2005018_task1.py
   python3 2005018_task2.py

   # In separate terminals, run Alice & Bob for ECDH:
   python3 2005018_task3_BOB.py
   python3 2005018_task3_ALICE.py


2. **Lab 2 (Website fingerprinting)**
  ```bash
  cd Offline2/starter_code/template
  
  # Create & activate a venv
  python3 -m venv venv
  source venv/bin/activate        # Linux/macOS
  # OR on Windows:
  # .\venv\Scripts\activate
  
  # Install dependencies
  pip install Flask selenium sqlalchemy torch torchvision matplotlib
  
  # Launch backend server
  python app.py
  
  # In another terminal:
  python collect.py
  
  # train models
  python train.py
