# one document per person with company embedded

import pymongo
from faker import Faker
import random
import time
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# connect to MongoDB
client = pymongo.MongoClient(f"mongodb://{config['connection']['host']}:{config['connection']['port']}/")
db = client[config['database']['name']]  # Use the database name from the config file
persons_col = db["persons_m2"]

# clean collection - to avoid issues when running multiple times 
persons_col.drop()

# initialize faker and set the amount of data to generate 
fake = Faker()
num_companies = 100
num_persons_per_company = 1000

# generate data for companies 
companies = []
for _ in range(num_companies):
    companies.append({"name": fake.company()})

# generate data for persons
persons = []
for company in companies:
    for _ in range(num_persons_per_company):
        birth_year = random.randint(1950, 2000)
        persons.append({
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "birth_year": birth_year,
            "age": 2024 - birth_year,
            "company": company}) # here we embed the company - so each person contains the entire 
                                 # company document. This means we are denormalizing 

# insert data into corresponding collection (only persons since company is embedded)
persons_col.insert_many(persons)

# Q1: For each person, retrieve their full name and their company's name
start = time.time()
# no joins needed since company data is embedded - we use the find() method
q1_results = persons_col.find(
    {},  # get all documents
    {
        "_id": 0,  # Exclude _id field
        "full_name": {"$concat": ["$first_name", " ", "$last_name"]},  
        "company.name": 1})  # Include company name 

q1_time = time.time() - start
print(f"Q1 execution time: {q1_time:.4f}s")

# Q2: For each company, retrieve its name and the number of employees
start = time.time()
pipeline = [
    {
        # Group by company name and count employees
        "$group": {
            "_id": "$company.name",        # Group by embedded company name
            "num_employees": {"$sum": 1}   # Count documents in each group
        }
    },
    {
        # project the output to renae the _id field
        "$project": {
            "_id": 0,                     
            "company_name": "$_id",       
            "num_employees": 1}}]          

q2_results = persons_col.aggregate(pipeline)
q2_time = time.time() - start
print(f"Q2 execution time: {q2_time:.4f}s")

# Q3: For each person born before 1988, update their age to "30"
start = time.time()
result_q3 = persons_col.update_many(
    {"birth_year": {"$lt": 1988}},  # Filter for persons born before 1988
    {"$set": {"age": 30}}           # Set age to 30
)
q3_time = time.time() - start
print(f"Q3 execution time: {q3_time:.4f}s")

# Q4: Update company names to include "Company"
start = time.time()
# Update embedded company name for all persons
persons_col.update_many(
    {},  # Update all documents
    [{"$set": {"company.name": {"$concat": ["$company.name", " Company"]}}}]  # Concatenate "Company" to embedded company name
)
q4_time = time.time() - start
print(f"Q4 execution time: {q4_time:.4f}s")
