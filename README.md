## Valentin Shorin - Social Network
___
### About
My aim is to create business level project, that may show business-oriented me and test my skills with language and frameworks.

Service that provide personal users blogs.
The user can register and create a page, going to which you can see all the author's records.
Registered users have the opportunity to subscribe to authors and leave comments to their records.
Unregistered users can only view authors and comments on them.

Tech: Python, Django, Django Rest Framework, DjangoORM, testing via Unittest, HTML-CSS layout basics

### Installation
###### 1. Clone repository
```
git clone https://github.com/vshorin-git/Social-Network && cd yatube
```
###### 2. Install virtual environment
```
python3 -m venv .env
source env/bin/activate
```
###### 3. Install python requirement modules
```
pip install -r requirements.txt
```
###### 4. Change your environment values
```
Create .env file in yatube/ with following content:
SECRET_KEY=')=(vp1)y(m0h2e86c01lm+$-72i#na)*i4e3$3@663re&_wx%4'
```
###### 5. Migrate and collect statics
```
python manage.py migrate
python manage.py collectstatic
```
###### 6. Create superuser
```
python manage.py createsuperuser
```
Create .env file with following content:
SECRET_KEY=')=(vp1)y(m0h2e86c01lm+$-72i#na)*i4e3$3@663re&_wx%4'
```
##### 7. Run project
```
python3 manage.py runserver
```
