# Komodore Auto Parts KG

### Prerequisites

- Python 3.8
- pip 23.2.1 (or later)
- Virtualenv 

## How To Run
1. Install `virtualenv`:
```
$ pip install virtualenv
```

2. Create a virtual environment:
```
$ virtualenv venv
```

3. Activate the virtual environment:
```
$ venv\Scripts\activate
```

4. Then install the dependencies:
```
$ (env) pip install -r requirements.txt
```

5. Apply Migrations:
```
$ (env) python manage.py migrate
```

6. Create a Superuser:
```
$ (env) python manage.py createsuperuser
```

7. Finally start the web server:
```
$ (env) python manage.py runserver
```

The app should now be running at http://127.0.0.1:8000/.
