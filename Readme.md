# Swiss Bird Occurrences Data Pipeline and Analysis

## Project Overview

This project provides an end-to-end data pipeline written in Python to fetch, process, and analyze bird occurrence data in Switzerland using the Global Biodiversity Information Facility (GBIF) REST API.

The pipeline performs the following tasks:

1. Queries the GBIF Occurrence Search API for bird observation records (Class Key `212`) in Switzerland (`CH`) for the target year `2015`.
2. Downloads paginated API responses in batches of 300 records and stores the raw responses as JSON files.
3. Loads, parses, and extracts selected fields from the raw JSON files, including custom extraction of media URLs.
4. Cleans and standardizes the dataset by renaming columns into human-readable names (for example, converting `key` to `gbif_occurrence_id`, `species` to `species_name`, and `decimalLatitude` to `latitude`).
5. Exports the cleaned dataset (limited to the first 1,000 records) as a CSV file for further analysis.
6. Includes a Jupyter Notebook (`test.ipynb`) for exploratory data analysis, including:
   - Top observed bird species
   - Number of observations per year
   - Count of records with unidentified species

---

## Required Tools and Dependencies

### System Requirements

- **Python:** Version **3.10** or higher (tested with Python **3.12**)
- **Jupyter Notebook** or **JupyterLab:** Required to run the exploratory analysis notebook (`test.ipynb`)

### Python Libraries

The project requires the following Python packages:

| Package | Purpose |
|---------|---------|
| **requests** | Sends HTTP requests to the GBIF REST API |
| **pandas** | Data cleaning, transformation, analysis, and CSV export |
| **pathlib** *(Standard Library)* | Cross-platform file and directory management |
| **json** *(Standard Library)* | Reading and writing JSON files |
| **numpy** | Numerical operations used by Pandas |
| **python-dateutil** | Date parsing utilities |
| **tzdata** | Time zone support |
| **packaging** | Package version handling |
| **six** | Python compatibility utilities |

---

## Project Structure

```text
.
├── data/
│   ├── raw/                          # Raw JSON files downloaded from the GBIF API
│   └── csv/                          # Cleaned CSV output
│       └── swiss_bird_occurrences.csv
│
├── app.py                            # Main ETL pipeline
├── test.ipynb                        # Exploratory Data Analysis notebook
├── requirements.txt                  # Project dependencies
├── .gitignore                        # Git ignore rules
└── README.md
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository.git

cd your-repository
```

### 2. Create a Virtual Environment

Windows

```bash
python -m venv .venv
```

Activate it:

**Command Prompt**

```bash
.venv\Scripts\activate
```

**PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

Run the main pipeline using:

```bash
python app.py
```

The application will:

1. Create the required project folders.
2. Fetch bird occurrence records from the GBIF API.
3. Save the raw responses as JSON files.
4. Load and merge all downloaded data.
5. Clean and standardize the dataset.
6. Export the processed data to CSV.
7. Display a preview of the resulting DataFrame.

---

## Output

### Raw Data

Downloaded API responses are stored in:

```text
data/raw/
```

Example:

```text
page_1.json
page_2.json
page_3.json
page_4.json
```


---

## Data Processing Workflow

The ETL pipeline consists of the following stages:

1. Fetch data from the GBIF REST API.
2. Handle pagination automatically.
3. Save raw API responses as JSON.
4. Load all JSON files.
5. Extract required fields.
6. Extract media URLs from nested objects.
7. Rename columns using standardized names.
8. Convert the data into a Pandas DataFrame.
9. Export the cleaned dataset as a CSV file.

---

## Exploratory Data Analysis

The `Q&A.ipynb` notebook demonstrates basic data exploration, including:

- Identifying the most frequently observed bird species.
- Summarizing observations by year.
- Counting records with missing or unidentified species.
- Inspecting the cleaned dataset using Pandas.

---

## Skills Demonstrated

This project demonstrates practical experience with:

- Python programming
- REST API integration
- ETL pipeline development
- JSON processing
- Data cleaning and transformation
- Data extraction
- File management with `pathlib`
- Data analysis using Pandas
- CSV generation
- Jupyter Notebook workflows

---

## Future Improvements

Potential enhancements include:

- Configurable country and year parameters.
- Command-line argument support.
- Logging and monitoring.
- Retry logic for failed API requests.
- Unit testing.
- Data validation.
- SQLite or PostgreSQL integration.
- Automated scheduling using Cron or Task Scheduler.
