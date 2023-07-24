# Foodgram

This project can help you finding recipes and dish ideas.
Hope it will help you!
To start using it you just have to register or login.
And now you are able to do whatever you like. 
Good luck!

## Tecnhologies:
- Python 3.10
- Django 4.0
- Django REST framework 3.13
- Nginx
- Docker
- Postgres


# How to run project locally

1. Download repository with any comfortable for you way

2. Open bash terminal (```Ctrl + Alt + T``` on Linux)

3. Navigate to ```foodgram-project-react/infra``` using ```cd``` command

4. Install docker/docker-compose ```sudo apt install docker.io docker-compose```

5. When you successfully downloaded packages, just runcommand ```sudo docker-compose up --build -d```. Wait until it's finished.

6. Run command ```sudo docker exec -it web bash```, it will open bash inside Django app container.

7. Now you have to run bunch of commands:
- ```python3 manage.py makemigrations & python3 manage.py migrate & python3 manage.py collectstatic & python manage.py loaddata fixtures.json```
(Just copy and paste, maybe you'll have to type Yes and press Enter)
- You  have made migrations and run them (setting up the database), 
created static files (for admin panel and api endpoints look fancy) and loaded ingredient's data. Also there is prebuild admin user. (Credentials on the bottom of README)

Now you can access your project on http://localhost 

## Your project is ready but you would like to know how to do some more stuff

- Create new admin user. Inside bash terminal of Django App (step 6) run ```python3 manage.py createsuperuser```. Now fill in all the credentials.

- Exit bash terminal, just type ```exit```

- To access admin panel go on http://localhost/admin/ fill in admin username and password. And you are able to do admin stuff :)

- To stop your project do step 3 and run ```sudo docker-compose stop```
