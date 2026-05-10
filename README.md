readme = """# 🧠 Mental Health Services Data Pipeline & Dashboard
### Project 3 of 3 | Role: Data Engineer | Domain: Healthcare

---

## 📌 What This Project Is About

The US government publishes annual data on every mental health 
facility in America — what services they offer, how many patients 
they serve, how many staff they have. The data arrives as separate 
files per year with inconsistent formats, duplicate records, and 
missing values.

This project builds an automated data pipeline that:
1. Ingests raw data from multiple yearly files automatically
2. Cleans and standardises inconsistent formats across years
3. Loads everything into a structured SQLite database
4. Serves a live interactive dashboard anyone can use

---

## 🏗️ Project Architecture
---

## 📂 Dataset

- **Source:** SAMHSA National Mental Health Services Survey (N-MHSS)
- **Coverage:** 2020, 2021, 2022
- **Size:** 2,400 facility records across 51 US states
- **Format:** Separate yearly files with inconsistent structure

---

## 🧹 Real Data Engineering Challenges Solved

| Problem | Solution |
|---|---|
| Different column names per year | Dynamic column standardisation |
| State codes in different cases (AL vs al) | String normalisation |
| Insurance stored as Yes/No/1/0/Y/N | Unified boolean mapping |
| 5% duplicate records per file | Deduplication on facility ID |
| Missing values in numeric columns | Median imputation per column |
| Services stored as comma separated text | Exploded into normalised table |

---

## 🗄️ Database Design

Three normalised tables:

**facilities** — who and where
- facility_id, state, facility_type, urban_rural
- accepts_insurance, operating_months, year

**capacity** — how much they handle
- patients_served, staff_count, bed_count
- patients_per_staff, num_services, is_overburdened

**services** — what they offer
- One row per service per facility (normalised)

---

## 📊 Dashboard Features

- **Summary metrics bar** — total facilities, patients, overburdened count
- **Tab 1: By State** — facility counts, patient volumes, insurance rates
- **Tab 2: By Facility Type** — type distribution, patient volumes, services
- **Tab 3: Trends Over Time** — how provision changed 2020-2022
- **Tab 4: Overburdened Facilities** — which states and types are under pressure
- **Sidebar filters** — filter everything by year, state, type, urban/rural

---

## 🔍 Key Findings

1. Overburdened facilities peaked in 2021 (190 facilities) — 
   consistent with post-COVID mental health demand surge
2. Wyoming shows highest average patients per facility — 
   suggesting rural facilities carry disproportionate load
3. Community Mental Health Centers offer the most services 
   on average but are also most frequently overburdened

---

## ⚙️ How To Run This Project

### Run the full pipeline (takes under 5 seconds):
### Launch the dashboard:
### Run individual steps:
---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| Python 3 | Main programming language |
| Pandas | Data manipulation and cleaning |
| SQLite3 | Lightweight production database |
| Streamlit | Interactive web dashboard |
| Plotly | Interactive charts |
| Zipfile | Reading compressed data files |

---

## 💡 Key Concepts Learned

| Concept | Plain English Meaning |
|---|---|
| Data Pipeline | Automated assembly line for data |
| Database Normalisation | Split data into logical tables to avoid repetition |
| ETL | Extract, Transform, Load — the 3 steps of every pipeline |
| Caching | Store results in memory so dashboard loads fast |
| Schema Design | Planning table structure before building |

---

*Part of a 3-project Health Data portfolio built over 8 weeks*
*Projects: Data Analysis → Data Science → Data Engineering*
"""
