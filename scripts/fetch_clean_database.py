#Importing the required libraries
import requests
import pandas as pd
import sqlite3 as sql
from zipfile import ZipFile
from io import BytesIO

#DATA IS IN THOUSANDS AND SEASONALLY ADJUSTED

#Fetching the data from the ONS website and saving it as a xls file
def fetch_data():
    url_industry = "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/workforcejobsbyindustryjobs02/current/jobs02sep2026.xls"
    response = requests.get(url_industry)
    with open('data/raw/industries02sep2026.xls', 'wb') as f:
        f.write(response.content)

    url_salary = "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/earningsandhoursworkedbyindustryandoccupationashetable29/2026provisional/ashetable292026provisional.zip"
    response = requests.get(url_salary)
    with ZipFile(BytesIO(response.content), "r") as z:
        with z.open('PROV - SIC07 Industry by Occupation SOC20 (2) Table 29.7a   Annual pay - Gross 2026.xlsx') as salary_industry:
            with open('data/raw/salaries_industries02sep2026.xlsx', 'wb') as f:
                f.write(salary_industry.read())

    print("\nData fetched successfully.")

#Cleaning data
def clean_data():
#Industry data
#Retriving the headers from the industries excel file and cleaning them up to be used as column names for the dataframe
    headers = pd.read_excel('data/raw/industries02sep2026.xls', sheet_name="WFJ SA", skiprows = 3, usecols = "A, C:X").columns.tolist()
    headers[0] = "Date"
    headers[4] = "Electricity, gas, steam & air conditioning supply"
    headers[9] = "Accommodation & food service activities"
    headers[15] = "Public admin & defence; compulsory social security"
    headers[20] = "Private households"
    headers[22] = "All Jobs"

    for i in range(len(headers)):
        headers[i] = headers[i].replace(",", ";")
        headers[i] = headers[i].strip()

    #Cleaning the dates of the dataframe and converting them to datetime format
    df_industry = pd.read_excel('data/raw/industries02sep2026.xls', sheet_name="WFJ SA", names = headers, header = None, skiprows = 5, usecols = "A, C:X", nrows = 193)
    df_industry["Date"] = df_industry["Date"].str.strip()
    df_industry.loc[df_industry["Date"] == "Mar 193", "Date"] = "Mar 19"
    df_industry.loc[df_industry["Date"] == "Mar 204", "Date"] = "Mar 20"
    df_industry.loc[df_industry["Date"] == "Mar 26 (r)", "Date"] = "Mar 26"
    df_industry.loc[df_industry["Date"] == "Jun 26 (p)", "Date"] = "Jun 26"
    df_industry["Date"] = pd.to_datetime(df_industry["Date"], format="%b %y")

    df_industry.to_csv('data/processed/industries02sep2026.csv', index=False)

    #Salary data
    #Retriving the necessay columns from the salary excel file and cleaning them up 
    df_salary = pd.read_excel('data/raw/salaries_industries02sep2026.xlsx', sheet_name="All", skiprows = 5, usecols = "A,F",  header = None, names = None)
    df_salary.iloc[:, 0] = df_salary.iloc[:, 0].str.strip()
    industries = [
        "Agriculture, Forestry And Fishing",
        "Mining And Quarrying",
        "Manufacturing",
        "Electricity, Gas, Steam And Air Conditioning Supply",
        "Water Supply; Sewerage, Waste Management And Remediation Activities",
        "Construction",
        "Wholesale And Retail Trade; Repair Of Motor Vehicles And Motorcycles",
        "Transportation And Storage",
        "Accommodation And Food Service Activities",
        "Information And Communication",
        "Financial And Insurance Activities",
        "Real Estate Activities",
        "Professional, Scientific And Technical Activities",
        "Administrative And Support Service Activities",
        "Public Administration And Defence; Compulsory Social Security",
        "Education",
        "Human Health And Social Work Activities",
        "Arts, Entertainment And Recreation",
        "Other Service Activities",
    ]

    df_salary = df_salary[df_salary.iloc[:, 0].isin(industries)]

    df_salary.iloc[:, 0] = df_salary.iloc[:, 0].str.replace(",", ";")
    df_salary.iloc[:, 0] = df_salary.iloc[:, 0].str.replace("And", "&")
    df_salary.iloc[:, 0] = df_salary.iloc[:, 0].str.capitalize()
    df_salary.columns = ["Industry", "Mean_Salary"]

    df_salary.to_csv('data/processed/salaries_industries02sep2026.csv', index=False)

    print("\nData cleaned successfully.")

#Putting the cleaned data into a SQLite database for easy access and retrieval

#Connection to SQLite database
def store_data_in_database():
    conn = sql.connect("data/processed/industries.db")
    df_industry = pd.read_csv('data/processed/industries02sep2026.csv')
    df_industry.to_sql("Industry_Jobs", conn, if_exists="replace", index=False)
    conn.close()

    conn = sql.connect("data/processed/salaries_industries.db")
    df_industry = pd.read_csv('data/processed/salaries_industries02sep2026.csv')
    df_industry.to_sql("Salaries_for_Industries", conn, if_exists="replace", index=False)
    conn.close()

    print("\nData stored in database successfully.")