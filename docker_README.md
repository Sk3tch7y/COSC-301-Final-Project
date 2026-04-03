# How to Run Docker!!

### 1) Make sure you have docker installed

![image](./Images/Screenshot%202026-03-28%20at%201.39.35 AM.png)

### 2) In the project path, call `docker compose up -d`

### 3) to verify connection open a docker bash `docker exec -it cosc_301_proj_postgres_1 bash`, and run `psql -h localhost -p 5432 -U postgres` and enter password. Then call `\dt transactions_data` you should see a table. You can also call, `\dt *` to see all tables.

### 4) You can also connect to database via interface application (try pgadmin)
