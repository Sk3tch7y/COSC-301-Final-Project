# How to Run Docker!!
### 1) Make sure you have docker installed

### 2) Under volume parameter in the compose yml file, change the path with the kaggle archive folder to your own path, see below. 
`
  volumes:
      ......
      - <MY_ARCHIVE_PATH>:/docker/data # IMPORTANT!!! Please change root to your own "archive" folder.
`
### 3) On this project's path, call `docker compose up -d`



### 3) Or Connect to database via interface application (try pgadmin)

### 5) For username in pgadmin, call `whoisme` on terminal, that's your username

