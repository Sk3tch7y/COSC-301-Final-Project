# How to Run Docker!!
### 1) Make sure you have docker installed

### 2) Under volume parameter in the compose yml file, change the path to your local archive folder path.. 

![image](./Images/Screenshot%202026-03-28%20at%201.39.35 AM.png)

### 3) In the project path, call `docker compose up -d`

### 4) to verify connection, call `psql -h localhost -p 5431 -U postgres` and enter password. Then call `\dt transactions_data` you should see a table. You can also call, `\dt *` to see all tables. 

### 5) You can also connect to database via interface application (try pgadmin)


