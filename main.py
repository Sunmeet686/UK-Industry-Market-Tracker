#Importing the required libraries
from scripts.fetch_clean_database import fetch_data, clean_data, store_data_in_database
from flask import Flask, render_template
from flask_cors import CORS
import sqlite3
import pandas as pd

app = Flask(__name__)
CORS(app)

#Creating different routes for the API to fetch the data from the database and return it as JSON
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/industries")
def get_industries():
    conn = sqlite3.connect("data/processed/industries.db")
    df = pd.read_sql("SELECT name FROM pragma_table_info('Industry_Jobs')", conn)
    df.drop(index = df[df['name'] == 'Date'].index, inplace=True)
    industries = df['name'].tolist()
    conn.close()
    return {"industries": industries}

@app.route("/api/industries/<industry_name>")
def get_industry_data(industry_name):
    industries = industry_name.split(",")
    columns_str = ", ".join(f'"{i}"' for i in industries)
    conn = sqlite3.connect("data/processed/industries.db")
    query = f'SELECT Date, {columns_str} FROM Industry_Jobs ORDER BY Date ASC'
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient="records")

@app.route ("/api/industries/<industry>/salary")
def get_salary_data(industry):
    conn = sqlite3.connect("data/processed/salaries_industries.db")
    query = f'SELECT Mean_Salary FROM Salaries_for_Industries WHERE Industry = "{industry}"'
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient="records")

if __name__ == "__main__":
    fetch_data()
    clean_data()
    store_data_in_database()

    app.run(debug=True, use_reloader=False)