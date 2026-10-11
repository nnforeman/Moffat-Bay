Moffat Bay Lodge

Requires: Python 3.9+, MySQL 8 (running), and a web browser.

1. Create the database

In MySQL (command line or Workbench), run:

CREATE DATABASE moffat_bay;
USE moffat_bay;
SOURCE C:/path/to/Group2_SQLFile.sql;

2. Install the Python packages

In a terminal, in the project folder run:
pip install -r requirements.txt

3. Add your database settings

Edit .env to include your username and password
and a SECRET_KEY (any long random text):

DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=moffat_bay
SECRET_KEY=any-long-random-text

4. Run the app in a terminal

python app.py

5. Open the website

Go to http://localhost:5000 in a browser