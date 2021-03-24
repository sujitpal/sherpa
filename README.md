# sherpa

Django based web application to help with organizing a conference (summit).

The webapp is currently not tied together because it serves as the dynamic backend for a Sharepoint based website.

## Instructions for setting up Dev Environment

* Create a fresh conda environment: `conda create -n django python=3.8.5`
* Switch to the environment and install packages listed in `requirements.txt`.
  * `conda activate django`
  * `pip install -r requirements.txt`
* Create the local SQLite3 database to back the application
  * `python manage.py makemigrations`
  * `python manage.py migrate`
  * `python manage.py createsuperuser`
* Load reference data: `python manage.py shell` and once in the shell.
  * `>>> import load_reference_data`
  * `>>> quit()`
* Make a folder to store speaker images: `mkdir -p media/avatars`.

## Instructions for Production Deployment

Instructions are based on actual deployment on an Amazon EC2 t3.large (2 vCPU, 8 GB RAM) with 50 GB disk, running Ubuntu 20.04. Commands may be slightly different for other platforms.

The production setup switches out the SQLite3 database with a PostgreSQl database backend. Instead of using `python manage.py runserver` we use gunicorn to start up the application on port 8080, then use Nginx reverse proxy to proxy port 8080 onto port 80. The security group 'HTTP over DC' is used to allow access to port 80 from anywhere within the VPN. In addition, the dummy email service that wrote emails to the log files has been replaced with an SMTP backend using a real gmail account. Finally, we also collect static files so the admin pages and application pages are able to access them a single location specified in Nginx.

### PostgreSQL backend setup

* We use instructions from Digital Ocean's [How To Use PostgreSQL with your Django Application on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04).
* Download necessary libraries for PostgreSQL
```
$ sudo apt-get update
$ sudo apt-get install python3-pip python3-dev libpq-dev
$ sudo apt-get install postgresql postgresql-contrib
```
* Create database and configure permissions.
```
$ sudo su - postgres
postgres$ psql
postgres=#
postgres=# create database sherpa_db;
CREATE DATABASE
postgres=# create user django with password 'sherpa';
CREATE ROLE
postgres=# alter role django set client_encoding to 'utf8';
ALTER ROLE
postgres=# alter role django set default_transaction_isolation to 'read committed';
ALTER ROLE
postgres=# alter role django set timezone to 'utc';
ALTER ROLE
postgres=# grant all privileges on database sherpa_db to django;
postgres=# \q
postgres@ip-10-169-23-250:~$ exit
logout
GRANT
```

git clone the application

Install libraries listed in requirements.txt using pip3

Update sherpa/settings.py as indicated with TODO: PROD and TODO: DEV comments

$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py createsuperuser
$ python3 manage.py shell
>>> import load_reference_data
>>> quit()

Rather than compile PostgreSQL driver psycopg2 from source, `pip install psycopg2-binary`, works fine for Ubuntu 20.04.

## Running under gunicorn

$ sudo apt install gunicorn
(base) ubuntu@ip-10-169-23-99:~/sherpa$ sudo /home/ubuntu/anaconda3/bin/gunicorn -b 10.169.23.99:80 sherpa.wsgi

gunicorn -w4 -b 0.0.0.0:8080 sherpa.wsgi

sudo cp gunicorn.service /etc/systemd/system/

sudo systemctl start gunicorn
sudo systemctl enable gunicorn

sudo systemctl status gunicorn
ls -l sherpa.sock

// logs
sudo journalctl -u gunicorn

// restart gunicorn
sudo systemctl daemon-reload   // if made changes to service file
sudo systemctl restart gunicorn


sudo apt install nginx
cp sherpa.nginx /etc/nginx/sites-available/sherpa

// validate configuration
sudo nginx -t

sudo systemctl restart nginx
sudo ufw allow 'Nginx Full'

https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04


-- email
https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab

-- collectstatic

set STATIC_ROOT in settings.py (temporarily)
python manage.py collectstatic
copy output into $PROJECT_HOME/static (replacing current)
https://docs.djangoproject.com/en/3.1/howto/static-files/deployment/

