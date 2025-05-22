# one document per company, with person embedded

import pymongo
from faker import Faker
import random
import time

# connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["lab2_db"]
companies_col = db["companies_m3"]

# clean collection - to avoid issues when running multiple times
companies_col.drop()

# initialize faker and set the amount of data to generate 
fake = Faker()
num_companies = 100
num_persons_per_company = 1000

# generate data for companies and persons
companies = []
for _ in range(num_companies):
    # creata data for persons for each company
    persons = []
    for _ in range(num_persons_per_company):
        birth_year = random.randint(1950, 2000)
        persons.append({
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "birth_year": birth_year,
            "age": 2024 - birth_year
        })
        # create the company document with all corresponding persons embedded
    companies.append({
        "name": fake.company(),
        "employees": persons}) # here we embed the persons - so each company contains an array with 1000 persons

# insert data into corresponding collection (only companies since persons are embedded)
companies_col.insert_many(companies)

# Q1: For each person, retrieve their full name and their company's name
start = time.time()
q1_results = companies_col.aggregate([
    {
        # creates one document per employee
        "$unwind": "$employees"},
    {    
        # Project the required fields from the separated documents just defined
        "$project": {
            "_id": 0,                                                              
            "full_name": {"$concat": ["$employees.first_name", " ", "$employees.last_name"]}, 
            "company_name": "$name"}}])    
                                        
q1_time = time.time() - start
print(f"Q1 execution time: {q1_time:.4f}s")

# Q2: For each company, retrieve its name and the number of employees
start = time.time()
q2_results = companies_col.aggregate([
    {
        # only projection since we just need the count
        "$project": {
            "_id": 0,                           
            "company_name": "$name",            
            "num_employees": {"$size": "$employees"}}}])

q2_time = time.time() - start
print(f"Q2 execution time: {q2_time:.4f}s")

# Q3: For each person born before 1988, update their age to "30"
start = time.time()
q3_results = companies_col.update_many(
    {},  # all company documents
    [
        {
            "$set": {
                "employees": {
                    # transform each element in the employees array
                    "$map": {
                        "input": "$employees",      # array to transform
                        "as": "e",                  # name for each array element
                        "in": {                     # Transformation for each element
                            "first_name": "$$e.first_name",   # Keep these 3 unchanged
                            "last_name": "$$e.last_name",     
                            "birth_year": "$$e.birth_year", 
                            "age": {
                                "$cond": [
                                    {"$lt": ["$$e.birth_year", 1988]},  # if birth_year < 1988
                                    30,                                   # set age to 30
                                    "$$e.age"]}}}}}}])                    # otherwise keep original value

q3_time = time.time() - start
print(f"Q3 execution time: {q3_time:.4f}s")

# Q4: Update company names to include "Company"  
start = time.time()
companies_col.update_many(
    {},  # all company documents
    [{"$set": {"name": {"$concat": ["$name", " Company"]}}}]  # Concatenate " Company" to company name
)
q4_time = time.time() - start
print(f"Q4 execution time: {q4_time:.4f}s")




