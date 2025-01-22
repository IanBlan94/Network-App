# NetQuizzer

## Overview
This Flask app helps users practice:
1. **Decimal-to-Binary Conversion**
2. **Binary-to-Decimal Conversion**
3. **Classful Address Analysis**
4. **Subnet Quiz**

Each module allows up to 3 attempts per question, with results stored in CSV files.

---

## Setup

### Prerequisites
- **Python Packages**: Install Flask and pandas:
  ```bash
  pip install flask pandas 

### Ensure these files exist:
    -app.py
    -templates/ (HTML files: main.html, decimaltobinary.html, binarytodecimal.html, classfuladdress.html, wildcardmask.html)
    -classaddress.py (classful address analysis quiz)
    -wildcard_mask.py (subnet quiz)
    -questions.csv (subnet quiz questions)

### Run the App:

python app.py -or- python -m app run

Open http://127.0.0.1:5000 in your browser.


## Navigate Between Games:

Decimal-to-Binary: Enter an 8-bit binary equivalent of the given decimal.
Binary-to-Decimal: Enter the decimal equivalent of the given binary.
Subnet Quiz: Answer randomly generated subnetting questions.
Game Rules:

Up to 3 attempts per question.
Results are saved to CSV files (decimal_to_binary_results.csv, binary_to_decimal_results.csv).

## Features
Session Tracking: Tracks attempts and game state.
Dynamic Storage: Automatically logs results into CSVs.
Customizable Templates: Modify the templates/ folder for design changes.

## Troubleshooting
Missing files? Ensure wildcard_mask.py and questions.csv are present.
Python 3.7+ is required.
Templates (main.html, etc.) must be in the templates/ directory.
