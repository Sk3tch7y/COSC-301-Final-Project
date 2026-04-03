# COSC 301 Final Project Proposal

## Project Background

Understanding spending behavior is important for businesses to remain competitive within the economic market. Analyzing when customers spend the most, their preferred transaction methods, and how spending varies across age groups can provide insights into financial trends and decision-making patterns. Following the financial recession, the 2010s provided insights into a period of economic recovery, during which customer spending began recovering. At the same time, advancements in technology led to a significant increase in online transactions and digital payment methods. These changes have reshaped how customers spend and manage their finances. By studying transaction data across this period, this project aims to better understand seasonal spending patterns, long-term trends, and demographic differences in financial behavior among age groups.

## Project Outline

### Project Title: Spending Across The 2010’s

Our Course Project uses the _Financial Transactions Dataset: Analytics_ (2009 - 2019) from Kaggle: https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets

The goal of our project is to extract data to visualize and understand changes in consumer spending behaviours over the course of a year and during periods of economic instability. We chose to use this dataset because it includes anonymized fincancial transaction records over a 10-year period, including details about whether the transaction was fraudulent. The dataset components consist of: transaction data, card information, merchant category codes, fraud labels, and user data.

The key features we will be focusing on are:

- Transaction amount
- Transaction date
- Transaction method (swipe, chip, online)
- User age
- Credit limit

This dataset is well suited for analyzing financial trends because it covers the economic recovery following the recession in 2009, and the greatest period of growth for online transactions (2010s).

## Major Questions

For this project, we have chosen to **extract** data to analyze and answer the following questions:

- What times of year are busiest for commerce?
- How does spending change in the years following a recession (2009 -> 2019)?
- How does the volume of online spending change as the internet matures?
- How spending changes across age groups on average (Who spends the highest percentage of their available credit)?

## Tools

For our project, we will use PostgreSQL, Python, and Microsoft Excel.

**PostgreSQL**  
Used to store and manage our cleaned data, allowing for efficient queries across the dataset.

**Python**  
Used to clean our data and perform data analysis. Python has financial analysis libraries making it ideal for our project.

**Tableau**  
Used for our final report and visualization. Paired with our use of Python, will make it easy to visualize and analyze our data further after filtering and cleaning of data.

## Data Pipeline

1. Data acquisition/loading  
   Download our dataset from Kaggle

2. ETL / cleaning  
   Remove missing values, duplicates, and any necessary outliers.

3. Storage of cleaned data  
   Store cleaned data in PostgreSQL

4. Exploratory Data Analysis (EDA)  
   Summary statistics and missingness analysis.  
   Distribution analysis of transactions.  
   Group transactions by age.

5. Reporting  
   Create visuals (graphs/dashboards) on Excel.

## Ethics and Considerations

Since our project uses anonymized transaction data, there are no privacy concerns for vendors/customers in any given transaction. Some ethical concern could be given to the usage of metrics extracted from this data, exploiting consumer spending habits can be considered unethical. This project deals purely with the analytical and offers no advice for exploiting consumer practices

The source dataset is licensed under the Apache 2.0 conditions, meaning we are free to use it given that our work also falls under the Apache 2.0 license.

# Project Setup:

## 1. Install dependencies and start virtual environment

Mac:

```{sh}

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

Windows:

```{sh}

python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

```

## 2. Install and start the docker engine:

```
https://docs.docker.com/engine/install/
```

## 3. Run the main.py file

```
    python main.py
```

Wait for it to complete. If interrupted delete the docker container and volume and restart

## 4. Install Tableau Desktop: [here](https://www.tableau.com/support/releases)

## 5. Open "report_visualizations.twb" in Tableau:

If the file doesnt connect to the container automatically, configure the connection with the following:

URL: jdbc:postgresql://127.0.0.1:5432/financial_data
Dialect: PostgreSQL
User: postgres
password: other_pw

Reports should automatically populate

### To access database manually use commands:

docker exec -it cosc_301_proj_postgres_1 bash

### then:

psql -h localhost -p 5432 -U postgres -d financial_data
