# Partisk
## Install
* Install python3, pip, django2, memcached (optional) and mysql/mariadb
* sudo apt-get install libmariadbclient-dev (mariadb) or sudo apt-get install libmysqlclient-dev (mysql)

* pip install virtualenv virtualenvwrapper
* source /usr/local/bin/virtualenvwrapper.sh
* mkvirtualenv -a /url/to/source -ppython3.6 partisk
* pip install -r python_requirements.txt

### Existing database
* Create a mysql database named partisk
* mysql -u username -p partisk < partisk.sql
* python manage.py migrate --fake-initial

### Clean database
* Create a mysql database named partisk
* python manage.py migrate

### Running the server
* python manage.py runserver --insecure
