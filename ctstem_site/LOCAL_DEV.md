Local Dev setup

Install python
----------------
  http://docs.python-guide.org/en/latest/starting/install/osx/

Install pip
--------------
  $ easy_install pip

Install virtual environment
----------------------------
  $ pip install virtualenv

Create your project folder in your home directory
--------------------------------------------------
  $ mkdir ct-stem
  $ cd ct-stem

In your project directory create a virtual environment
-----------------------------------------------------
  $ virtualenv venv

Activate the virtual environment
---------------------------------
  $ source venv/bin/activate

The name of the virtual environment will appear on the left prompt

Clone the project git repo
-----------------------------------------------------
  $ git clone git@github.com:snpradhan/ct-stem.git
  You will need to be added as a collaborator on the git repo
  Get the latest version of the repo
  $ git pull
  Create a new branch for local development
  $ git checkout -b local_dev

Install the requirements in the requirements.txt file
-----------------------------------------------------
  $ pip install -r requirements.txt

Install Postgresql
--------------------
  Follow the link below to install Postgres db
  https://postgresapp.com/
  Keep note of the postgres root user/password, database name, username and password

Creating base_settings.py
--------------------------
  settings.py contains all the project configuration. settings.py imports from base_settings.py
  $ cd ctstem_site/ctstem_site
  $ vi settings.py
  Comment out this line DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
  Create base_settings.py.  This file is not in the repo
  $ vi base_settings.py
  This is a local settings file containing the db password and other credentials.  This file is not checked into the repo.  Ask the developer for the content of this file.


Create database models
-----------------------
  $ cd ~/ct-stem/ctstem_site
  $ python manage.py migrate

  Later during development whenever there is a change in the model, apply the db changes as follows
  $ python manage.py makemigrations
  $ python manage.py migrate


Creating an admin user
-----------------------
First we’ll need to create a user who can login to the admin site. Run the following command:

  $ python manage.py createsuperuser
  Enter your desired username and press enter.

  Username: admin
  You will then be prompted for your desired email address:

  Email address: admin@example.com
  The final step is to enter your password. You will be asked to enter your password twice, the second time as a confirmation of the first.

  Password: **********
  Password (again): *********
  Superuser created successfully.

Run the server
----------------
  $ python manage.py runserver

The site is available at http://localhost:8000

The admin login is at http://localhost:8000/admin/
