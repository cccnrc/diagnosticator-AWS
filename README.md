### install docker: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html

### on server
APP_DIR='<path-to-folder>'    ### this is the DIR in which you deploy the APP
cd $APP_DIR

git clone .
docker-compose up --build


### NON-COMPOSE deploy
SQL_DB_DIR='<path-to-folder-for-MySQL-DB>'
### install mysql from docker and attach to a local DIR for DB
docker pull mysql/mysql-server
docker run --name=mysql -p 3306:3306 -v "${SQL_DB_DIR}":/var/lib/mysql -d mysql/mysql-server
sleep 10  # wait until deployed
MYSQL_ROOT_PWD=$( docker logs mysql 2>&1 | grep GENERATED | cut -d':' -f2 | tr -d ' ' )
docker exec -it mysql mysql -uroot -p"${MYSQL_ROOT_PWD}"
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
CREATE USER 'root'@'%' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
CREATE USER 'diagnosticator'@'%' IDENTIFIED BY 'diagnosticator';
GRANT ALL PRIVILEGES ON * . * TO 'diagnosticator'@'%';
FLUSH PRIVILEGES;
### LOGOUT
docker exec -it mysql mysql -udiagnosticator -pdiagnosticator
CREATE DATABASE diagnosticator;
### deploy th FLASK app
cd $APP_DIR
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
### activate
source venv/bin/activate
# sudo apt-get install -y libmysqlclient-dev
sudo yum install -y mysql-devel
venv/bin/pip install -r requirements3.txt
venv/bin/pip install gunicorn pymysql
flask db init
flask db migrate
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - main:app
