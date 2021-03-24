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
GRANT
postgres=# \q
postgres@ip-10-169-23-250:~$ exit
logout
$
```

### Email Backend

I needed to set up an additional Gmail email id under my account and set up an application key. This application key needs to be updated into the `prod_config/settings.py` file (see next point for details). Instructions were adapted from the article [How to send mail with Django and Gmail in production the right way](https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab).

### Download and setup Application

* Git clone application (using https): `git clone https://github.com/sujitpal/sherpa.git`
* Install libraries listed in requirements.txt using `pip3`. Most instructions ask you to `pip3 install psycopg2` but that requires gcc and compiling and failed for the couple of times I tried it, but `psycopg2-binary` is precompiled and works great.
```
pip3 install django
pip3 install django-plotly-dash
pip3 install Pillow
pip3 install psycopg2-binary
```
* Update production files in `prod_configs` folder with appropriate values for placeholder apps (they look like `__PLACEHOLDER__`)
* Copy the production settings.py file: `cp prod_configs/settings.py sherpa/settings.py`
* Apply database changes and set up admin user.
```
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py createsuperuser
```
* Load reference data
```
$ python3 manage.py shell
>>> import load_reference_data
>>> quit()
```

### Running under gunicorn

* Download gunicorn using apt: `sudo apt install gunicorn`
* Check that the command works (this is the gunicorn equivalent of `python3 manage.py runserver`), so idea is to forward port 8080 and see if the application comes up on the browser: `gunicorn -w4 -b 0.0.0.0:8080 sherpa.wsgi`
* We want to run gunicorn as a daemon, so copy the provided .service file to the appropriate location: `sudo cp prod_configs/gunicorn.service /etc/systemd/system/`
* Start gunicorn daemon and enable automatic restart across system reboots.
```
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```
* Check status of gunicorn: `sudo systemctl status gunicorn` and verify that the Unix socket file is created in local directory: `ls -l sherpa.sock`.
* You can paginate through gunicorn logs using `sudo journalctl -u gunicorn`
* If you need to make changes to the gunicorn.service file, then you need to `sudo systemctl daemon-reload` and restart (next point).
* If you change the application and need to see changes show up, you need to `sudo systemctl restart gunicorn`

### Setting up Nginx reverse proxy

Instructions for this were adapted from [this DigitalOcean article](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04).

* Install nginx: `sudo apt install nginx`
* Copy configuration for app: `cp sherpa.nginx /etc/nginx/sites-available/sherpa`
* Validate configuration: `sudo nginx -t`
* Restart nginx: `sudo systemctl restart nginx`
* Add rule for Nginx to firewall: `sudo ufw allow 'Nginx Full'`

### CSS visibility in Application and Admin pages

Admin pages are messed up because the CSS for the admin pages are packaged in the Django contrib library and not directly accessible as files, so Nginx cannot see them. To fix this, we need to merge the admin and application CSS on our Dev environment and push it up to the Prod environment. Instructions are adapted from [Django documentation on Deploying static files](https://docs.djangoproject.com/en/3.1/howto/static-files/deployment/).

* Set STATIC_ROOT=/full/path/to/project/static2 in settings.py (temporarily). This is a new sibling directory that will be generated and pushed to the prod environment, then deleted.
* Merge application and admin CSS files __on Dev environment__ using: `python manage.py collectstatic`
* Tar the `static2` folder and push to production: `tar cvzf static2.tar.gz static2/*`
* Untar __on Prod environment__ and overwrite the static subdirectory.
```
$ tar xvf static2.tar.gz
$ mv static static0; mv static2 static; rm -rf static0
```
