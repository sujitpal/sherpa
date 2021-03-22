# sherpa

Django based web application to help with organizing a conference (summit).

The webapp is currently not tied together because it serves as the dynamic backend for a Sharepoint based website.

## Instructions for setting up dev environment

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
