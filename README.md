# COSC 301 Final Project Proposal

## Project Outline

### Project Title: Spending Across The 2010’s

Our Course Project uses the *Financial Transactions Dataset: Analytics* (2009 - 2019) from Kaggle: https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets

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

**Excel**  
Used for our final report and visualization. Paired with our use of Python, will make it easy to visualize and analyze our data further.

## Data Pipeline

1) Data acquisition/loading  
Download our dataset from Kaggle

2) ETL / cleaning  
Remove missing values, duplicates, and any necessary outliers.

3) Storage of cleaned data  
Store cleaned data in PostgreSQL  

4) Exploratory Data Analysis (EDA)  
Summary statistics and missingness analysis.  
Distribution analysis of transactions.  
Group transactions by age.  

5) Reporting  
Create visuals (graphs/dashboards) on Excel.

## Ethics and Considerations

Since our project uses anonymized transaction data, there are no privacy concerns for vendors/customers in any given transaction. Some ethical concern could be given to the usage of metrics extracted from this data, exploiting consumer spending habits can be considered unethical. This project deals purely with the analytical and offers no advice for exploiting consumer practices

The source dataset is licensed under the Apache 2.0 conditions, meaning we are free to use it given that our work also falls under the Apache 2.0 license.
