# BDM Lab 2 - MongoDB Data Modeling Comparison

This project demonstrates three different data modeling approaches in MongoDB for managing company-employee relationships and compares their performance characteristics.

## Overview

The project implements and benchmarks three distinct MongoDB data modeling strategies:
1. **Normalized (M1)**: Separate collections with references
2. **Denormalized 1, Company documents embedded (M2)**: Person documents with embedded company data
3. **Denormalized 2, Person documents embedded (M3)**: Company documents with embedded employee arrays

Each approach executes the same four queries to compare performance and complexity trade-offs.

## Requirements

### Software Dependencies
- **MongoDB Community Server** (v8.0.9 or compatible)
- **MongoDB Shell (mongosh)** (v2.5.1 or compatible)
- **Python** (v3.10+ recommended)

### Python Packages
```bash
pip install pymongo faker
```

### System Setup
1. Download and extract MongoDB Community Server and MongoDB Shell
2. Add MongoDB binaries to your PATH:
   ```bash
   export PATH="$HOME/path/to/mongodb/bin:$PATH"
   export PATH="$HOME/path/to/mongosh/bin:$PATH"
   ```
3. Create data directory: `mkdir -p data/db`

## Quick Start

1. **Start MongoDB server:**
   ```bash
   ./start_mongo.sh
   ```

   This will create a connection to the database, which must be open (in a separate terminal window) to run the Python scripts of the different models.
   
2. **Run the modeling experiments:**
   
   ```bash
   python m1.py  # Normalized model
   python m2.py  # Denormalized model 1 (Company embedded)  
   python m3.py  # Denormalized model 2 (Person embedded)
   ```
   
   Once you run the scripts, you can establish the connection with MongoDB Compass and see the data that have been created. Just press ’add new connection’ and leave the default port that you see
   
3. **Stop MongoDB server:**
   ```bash
   ./stop_mongo.sh
   ```
   
   Or, in the terminal window where the connection is running, execute Ctrl + C.

## Data Models

### M1: Normalized Model ([m1.py](m1.py))
**Collections:** `companies_m1`, `persons_m1`

**Structure:**
```javascript
// companies_m1
{
  "_id": ObjectId("..."),
  "name": "Company Name"
}

// persons_m1  
{
  "_id": ObjectId("..."),
  "first_name": "John",
  "last_name": "Doe", 
  "birth_year": 1985,
  "age": 39,
  "company_id": ObjectId("...")  // Reference to company
}
```

**Characteristics:**

- ✅ No data duplication
- ✅ Easy to update company information
- ❌ Requires joins for most queries
- ❌ More complex aggregation pipelines

### M2: Denormalized Model 1 ([m2.py](m2.py))
**Collection:** `persons_m2`

**Structure:**
```javascript
// persons_m2
{
  "_id": ObjectId("..."),
  "first_name": "John",
  "last_name": "Doe",
  "birth_year": 1985, 
  "age": 39,
  "company": {           // Embedded company document
    "name": "Company Name"
  }
}
```

**Characteristics:**
- ✅ Fast person-centric queries (no joins)
- ✅ Simple query structure
- ❌ Company data duplicated across employees
- ❌ Company updates require updating all employee documents

### M3: Denormalized Model 2 ([m3.py](m3.py))
**Collection:** `companies_m3`

**Structure:**
```javascript
// companies_m3
{
  "_id": ObjectId("..."),
  "name": "Company Name",
  "employees": [         // Array of embedded employee documents
    {
      "first_name": "John",
      "last_name": "Doe",
      "birth_year": 1985,
      "age": 39
    },
    // ... more employees
  ]
}
```

**Characteristics:**
- ✅ Fast company-centric queries
- ✅ Single document per company
- ❌ Large document sizes (1000+ employees per company)
- ❌ Complex employee updates
- ❌ Document size limitations may be reached

## Benchmark Queries

Each model executes four standardized queries with performance timing:

1. **Q1**: For each person, retrieve their full name and their company’s name.
2. **Q2**: For each company, retrieve its name and the number of employees.
3. **Q3**: For each person born before 1988, update their age to “30”.
4. **Q4**: For each company, update its name to include the word “Company”.

## Dataset

- **Companies**: 100 companies with fake names
- **Employees**: 1,000 employees per company (100,000 total)
- **Employee data**: First name, last name, birth year (1950-2000), calculated age

## Performance Considerations

**Expected Performance Patterns:**

- **M1 (Normalized)**: Slower for queries requiring joins, efficient for updates
- **M2 (Denormalized 1)**: Fast person lookups, expensive company-wide operations  
- **M3 (Denormalized 2)**: Fast company operations, memory-intensive, complex employee updates

## File Structure

```
BDM-lab2/
├── README.md           # This file
├── m1.py              # Normalized model implementation
├── m2.py              # Denormalized model implementation  
├── m3.py              # Embedded model implementation
├── start_mongo.sh     # Start MongoDB server
├── stop_mongo.sh      # Stop MongoDB server
├── helper.ipynb       # Setup instructions notebook
├── data/              # MongoDB data directory
└── .gitignore         # Git ignore rules
```

## Usage Notes

- Each script drops existing collections before running to ensure clean state
- Performance timings are printed for each query
- Scripts can be run multiple times for performance comparison
- MongoDB server must be running before executing Python scripts

## Troubleshooting

**MongoDB won't start:**
- Ensure data directory exists: `mkdir -p data/db`
- Check if MongoDB is already running: `ps aux | grep mongod`
- Try manual start: `mongod --dbpath ./data/db`

**Import errors:**
- Install required packages: `pip install pymongo faker`
- Verify Python version compatibility

**Connection errors:**

- Confirm MongoDB is running on localhost:27017
- Check firewall settings if applicable

