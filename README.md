# DIAGNOSTICATOR SERVER - AWS

## INSTALLATION

### 1. DOCKER-COMPOSE

#### if it works this is the most straightforward way (need to have docker installed)
```
APP_DIR="<path-to-folder>"    ### choose the DIR in which you deploy the APP
cd $APP_DIR
git clone https://github.com/cccnrc/diagnosticator-AWS
docker-compose up --build
```

### 2. NON-COMPOSE deploy
```
### deploy MySQL with Docker
SQL_DB_DIR="<path-to-folder-for-MySQL-DB>"
docker pull mysql/mysql-server
docker run --name=mysql -p 3306:3306 -v "${SQL_DB_DIR}":/var/lib/mysql -d mysql/mysql-server
sleep 10  # wait until deployed
MYSQL_ROOT_PWD=$( docker logs mysql 2>&1 | grep GENERATED | cut -d':' -f2 | tr -d ' ' )

#### create MySQL users on docker
docker exec -it mysql mysql -uroot -p"${MYSQL_ROOT_PWD}"
#   pass these commands inside docker
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
CREATE USER 'root'@'%' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
CREATE USER 'diagnosticator'@'%' IDENTIFIED BY 'diagnosticator';
GRANT ALL PRIVILEGES ON * . * TO 'diagnosticator'@'%';
FLUSH PRIVILEGES;
# LOGOUT and LOGIN to create MySQL-DB on docker
docker exec -it mysql mysql -udiagnosticator -pdiagnosticator
CREATE DATABASE diagnosticator;

### deploy the app
cd $APP_DIR
git clone https://github.com/cccnrc/diagnosticator-AWS
python3.8 -m venv venv
echo 'export MAIL_SERVER=
export MAIL_PORT=
export MAIL_USERNAME=
export MAIL_PASSWORD=
export MAIL_USE_TLS=1
export MAIL_USE_SSL=0
export TOKEN_RESTORE_EXP_SEC=3600
export TOKEN_EXP_SEC=3600
export DATABASE_URL=mysql+pymysql://diagnosticator:diagnosticator@localhost:3306/diagnosticator' >> venv/bin/activate

### activate virtual environment
source venv/bin/activate
sudo yum install -y mysql-devel
venv/bin/pip install -r requirements.txt
venv/bin/pip install gunicorn pymysql
flask db init
flask db migrate
flask db upgrade

### start serving app on port 5000
exec gunicorn -b :5000 --access-logfile - --error-logfile - main:app
```


### AWS-SERVER
```
git clone https://github.com/cccnrc/diagnosticator-AWS.git
cd /home/enrico/columbia/diagnosticator-AWS/diagnosticator-server-AWS-00-LOCAL
```
