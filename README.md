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
MYSQL_ROOT_PWD=$( docker logs mysql 2>&1 | grep GENERATED | cut -d':' -f2,3,4,5,6 | tr -d ' ' )

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

### access MYSQL-DB
docker exec -it mysql mysql -udiagnosticator -pdiagnosticator
```


### AWS-SERVER
```
APP_DIR="/home/ec2-user/diagnosticator-server-AWS/diagnosticator-AWS"   # put yours DIR here
git clone https://github.com/cccnrc/diagnosticator-AWS.git
cd ${APP_DIR}
vim venv/bin/activate                     # store your credentials and other environment variables
gunicorn -b 0.0.0.0:8001 -w 1 main:app    # check APP

### GUNICORN
vim ${APP_DIR}/gunicorn_conf.py                          # edit gunicorn configuration to match your system
sudo vim /etc/systemd/system/diagnosticator.service      # create systemd service (store here ENV variables)
sudo systemctl daemon-reload
sudo systemctl start diagnosticator
sudo systemctl enable diagnosticator
sudo systemctl status diagnosticator
sudo systemctl restart diagnosticator

### NGINX
cd ~
amazon-linux-extras list | grep nginx               # check available options
sudo amazon-linux-extras install nginx1             # actually install it
sudo vim /etc/nginx/nginx.conf                      # default NGINX conf file
sudo vim /etc/nginx/conf.d/diagnosticator.conf      # create the NGINX conf file
sudo nginx -t                                       # check it works fine
sudo service nginx reload                           # restart nginx

### to let NGINX serve static files directly you need to add your user to www-data and chown of the DIR:
sudo usermod -a -G ec2-user www-data
sudo chown -R :www-data  /home/ec2-user/diagnosticator-server-AWS/diagnosticator-AWS/app/static


### APP UPDATES
cd $APP_DIR
git pull
sudo systemctl daemon-reload
sudo systemctl restart diagnosticator
sudo service nginx reload
```
