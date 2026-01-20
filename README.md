
# 📊 Sales Analytics System  
<div align="right">

**Student Name:** Rohit Kumar Jain  
**Student ID:** BITSoM_BA_25071652  
**Email:** devsuman1957@gmail.com  
**Date:**  Jan-20-2026  

</div>

---

## 📘 Project Overview

This project is completed as part of the **Python Programming / Data Analytics coursework**.  
The objective of this assignment is to design and implement a **Sales Data Analytics System** capable of handling **real-world messy data**, performing **data validation**, **data enrichment via external APIs**, and generating **business-ready analytical reports**.

The system processes raw, pipe-delimited sales files, cleans and validates records, enriches transactions using an external product API, performs analytical computations, and produces structured outputs suitable for decision-making.

> 📌 **Summary:**  
> This project demonstrates end-to-end data processing — from raw ingestion to analytics and reporting — using modular Python design, API integration, and robust data quality handling.

---

## 📂 Project Structure

```
sales-analytics-system/
├── README.md
├── main.py
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── file_handler.py
│   ├── data_processor.py
│   ├── api_handler.py
│   └── report_generator.py
├── data/
│   └── sales_data.txt
└── output/
```

---

## 🛠 Technologies Used

```
🐍 Python 3
📊 Pandas
🌐 REST API (DummyJSON)
📁 File handling & encoding management
📈 Data analytics & reporting
```

---

## 🧩 System Capabilities (10 Key Points)

1. Reads **messy pipe-delimited sales files** with multiple encoding fallbacks  
2. Cleans numeric fields by removing commas and formatting inconsistencies  
3. Validates transactions using **strict business rules**  
4. Supports **optional user-defined filters** (region, min amount, max amount)  
5. Calculates **regional sales performance**  
6. Identifies **top-selling products and customers**  
7. Detects **peak sales day and daily sales trends**  
8. Flags **low-performing products** for business insights  
9. Enriches transactions using **DummyJSON Products API**  
10. Generates a **professional multi-section analytical report** automatically  

---

## ▶️ How to Run the Project

### 1) Create a virtual environment (recommended)

**Windows (PowerShell):**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run

From the **repository root**:

```bash
python main.py
```

The program will:
- Ask if you want to apply filters (region / min amount / max amount)
- Create:
  - `data/enriched_sales_data.txt`
  - `output/sales_report.txt`

---

## Notes (Assignment Requirements)

- No hardcoded absolute file paths (paths are built relative to the project root)
- Handles encoding issues by trying: `utf-8`, `latin-1`, `cp1252`
- Removes commas from ProductName and numeric fields (e.g., `1,500` -> `1500`)
- Validation rules:
  - Quantity > 0
  - UnitPrice > 0
  - Required fields present
  - TransactionID starts with `T`
  - ProductID starts with `P`
  - CustomerID starts with `C`
- DummyJSON API:
  - Base URL: `https://dummyjson.com/products`
  - Fetch all products with `limit=100`

---

## Output Files

- `data/enriched_sales_data.txt` contains all original fields +:
  - `API_Category`, `API_Brand`, `API_Rating`, `API_Match`

- `output/sales_report.txt` contains 8 report sections in the required order.
# Sales Analytics System

A Python **Sales Data Analytics System** that:

- Reads and cleans messy pipe-delimited sales files (encoding handling + data issues)
- Validates and optionally filters transactions (region + amount range)
- Performs sales analytics (region performance, top products, customer analysis, daily trends, peak day, low performers)
- Fetches product details from the **DummyJSON Products API**
- Enriches sales transactions with API fields and saves a new file
- Generates a professional text report with **8 required sections**

## Repository Structure

```
sales-analytics-system/
├── README.md
├── main.py
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── file_handler.py
│   ├── data_processor.py
│   ├── api_handler.py
│   └── report_generator.py
├── data/
│   └── sales_data.txt
└── output/
```

## Setup

### 1) Create a virtual environment (recommended)

**Windows (PowerShell):**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

## Run

From the **repository root**:

```bash
python main.py
```

The program will:
- Ask if you want to apply filters (region / min amount / max amount)
- Create:
  - `data/enriched_sales_data.txt`
  - `output/sales_report.txt`

## Notes (Assignment Requirements)

- No hardcoded absolute file paths (paths are built relative to the project root)
- Handles encoding issues by trying: `utf-8`, `latin-1`, `cp1252`
- Removes commas from ProductName and numeric fields (e.g., `1,500` -> `1500`)
- Validation rules:
  - Quantity > 0
  - UnitPrice > 0
  - Required fields present
  - TransactionID starts with `T`
  - ProductID starts with `P`
  - CustomerID starts with `C`
- DummyJSON API:
  - Base URL: `https://dummyjson.com/products`
  - Fetch all products with `limit=100`

## Output Files

- `data/enriched_sales_data.txt` contains all original fields +:
  - `API_Category`, `API_Brand`, `API_Rating`, `API_Match`

- `output/sales_report.txt` contains 8 report sections in the required order.
