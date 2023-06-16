This is simple Django REST Framework application.
Steps to run the app:

1. Clone the repository

git clone: https://github.com/zejd/django-api

2. Create your own virtual environment

python3 -m venv venv
source venv/bin/activate

3. Install your requirements

pip install -r requirements.txt

4. Make your migrations

python manage.py makemigrations
python manage.py migrate

5.Create a new superuser

python manage.py createsuperuser

6. Run the app

python manage.py runserver

That’s it!
