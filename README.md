# Diagnosticator Server

This is the repository for the Server-side of the application, the same you find at [diagnosticator.com](https://diagnosticator.com)

Deploying this application you will have a personal copy of our server-side application and will be able to make any improvement, addition, change, etc. that you'd like to suggest to diagnosticator

To install this application you need [Docker](https://www.docker.com/) and [Flask](https://flask.palletsprojects.com/en/2.0.x/) on your machine. You will use them to deploy MySQL and the diagnosticator application.

To safely expose it to the outer world you will need [Nginx](https://www.nginx.com/) and [Gunicorn](https://gunicorn.org/)

This guide is based on [AWS](https://aws.amazon.com/), on which we are currently hosting our server. To deploy it based on other OS you will need to adapt the server commands (e.g. `yum install` with `apt install` in case you are running [Ubuntu](https://ubuntu.com/) etc.)



Here the steps to follow for the installation:

1. deploy MySQL through Docker (you can also use a local MySQL running version, just need to point the application to it through `DATABASE_URL` environment variable):
```
SQL_DB_DIR="<path-to-folder-for-MySQL-DB>"
docker pull mysql/mysql-server
docker run --name=mysql -p 3306:3306 -v "${SQL_DB_DIR}":/var/lib/mysql -d mysql/mysql-server
sleep 10  # wait until deployed
MYSQL_ROOT_PWD=$( docker logs mysql 2>&1 | grep GENERATED | cut -d':' -f2,3,4,5,6 | tr -d ' ' )
```
please note: change `<path-to-folder-for-MySQL-DB>` to whatever directory you want to use to store SQL DB locally

2. log into MySQL docker:
```
# access MySQL docker
docker exec -it mysql mysql -uroot -p"${MYSQL_ROOT_PWD}"
```

3. create diagnosticator database and give access to diagnosticator user:
```
# pass these commands inside MySQL docker
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
CREATE USER 'root'@'%' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
CREATE USER 'diagnosticator'@'%' IDENTIFIED BY 'diagnosticator';
GRANT ALL PRIVILEGES ON * . * TO 'diagnosticator'@'%';
FLUSH PRIVILEGES;
# LOGOUT and LOGIN to create MySQL-DB on docker
docker exec -it mysql mysql -udiagnosticator -pdiagnosticator
CREATE DATABASE diagnosticator;
```

4. clone the application
```
### deploy the app
APP_DIR="<path-to-folder>"    ### choose the DIR in which you deploy the APP
cd $APP_DIR
git clone https://github.com/cccnrc/diagnosticator-AWS
python3.9 -m venv venv        ### you need python3.9 and venv module installed
```

5. set the environment variables (use your own mail configuration for the application to be able to send e-mails, e.g. [mailtrap](https://mailtrap.io/blog/flask-email-sending/#:~:text=Email%20sending%20in%20Flask%2DMail,instance%20of%20a%20Mail%20class.&text=We'll%20need%20to%20set,from%20the%20other%20side!'), [gmail](https://overiq.com/flask-101/sending-email-in-flask/), etc.):
```
echo '
export MAIL_SERVER=<your-mail-server>
export MAIL_PORT=<your-mail-port>
export MAIL_USERNAME=<your-mail-username>
export MAIL_PASSWORD=<your-mail-password>
export MAIL_USE_TLS=1
export MAIL_USE_SSL=0
export TOKEN_RESTORE_EXP_SEC=3600
export TOKEN_EXP_SEC=3600
export DATABASE_URL=mysql+pymysql://diagnosticator:diagnosticator@localhost:3306/diagnosticator
' >> venv/bin/activate
```
please note: these variables will be automatically loaded at every `venv` activation:
```
source venv/bin/activate
```

6. install application requirements:
```
sudo yum install -y mysql-devel
venv/bin/pip install -r requirements.txt
venv/bin/pip install gunicorn pymysql
```

7. create application tables:
```
flask db init
flask db migrate
flask db upgrade
```

8. if you want to launch the application directly from terminal to give it a try (this will serve application on port `8001`, change it as you wish):
```
gunicorn -b :8001 --access-logfile - --error-logfile - main:app
```

Please Note: in case you want to locally deploy the application and edit files etc. you can just go to [http://localhost:8001](http://localhost:8001) on your browser and interact with the application. You will need to reload it (thorugh the `gunicorn` command above) if you make changes. :sunglasses:

You don't need to go through all the rest of those point (9. and below, that require a minimum of networking knowledge) unless you wish to setup a proper service exposed to the outer world (internet) with your [Diagnosticator](https://diagnosticator.com) server application.

In case you really wish this, here are the instructions:

9. serve the application to the outer world, configure Gunicorn:
```
vim ${APP_DIR}/gunicorn_conf.py                          # edit gunicorn configuration to match your configuration
sudo vim /etc/systemd/system/diagnosticator.service      # edit and creete service to match your configuration
sudo systemctl daemon-reload
sudo systemctl enable diagnosticator
sudo systemctl start diagnosticator
```
in this step we are basically creating a [systemd](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system_administrators_guide/chap-managing_services_with_systemd) service (called `diagnosticator`) that will responsible to actually run the application for us (otherwise we would need to be constantly ssh-connected to the server running the application in terminal). We configure Gunicorn through `gunicorn_conf.py` and `systemd` service though `diagnosticator.service`:
- you have an example of `gunicorn_conf.py` in this repo, change variables to match your configuration
- you have an example of `diagnosticator.service` in this repo, change variables to match your configuration
After configuration, we just reload all services to make the machine recognizing `diagnosticator` service (`sudo systemctl daemon-reload`) and with the last commands we just tell the server to automatically load `diagnosticator` service at boot (`systemctl enable`) and to actually start it (`systemctl start`).
After this, `diagnosticator` service will be running our application for us on the port we specified in `bind` inside `gunicorn_conf.py` (`8001` if you didn't change it)
A couple of other useful commands are:
```
sudo systemctl status diagnosticator       ### to check the service status
sudo systemctl restart diagnosticator      ### to restart the service and load changes you make to the application
```

10. serve the application to the outer world, configure Nginx:
```
amazon-linux-extras list | grep nginx               # check available options
sudo amazon-linux-extras install nginx1             # actually install it
sudo vim /etc/nginx/conf.d/diagnosticator.conf      # create the Nginx .conf file
sudo nginx -t                                       # check Nginx configuration file works fine
sudo service nginx reload                           # restart Nginx
```
Nginx manages internet traffic to your machine (to word this very basically). You have an example of `diagnosticator.conf` in this repo, this is intended to make your machine redirect any possible request to `https://` (to avoid unsafe `http://` traffic) and to serve on port `443` (`https` default port) your application (through `proxy_pass http://localhost:8001;`), thus any request made to your server IP address will be redirected to your application in `SSL` mode.
In order for this configuration to work, you need an SSL certificate (that you will point Nginx to through: `ssl_certificate` variable). To obtain one you can use: [Certbot](https://certbot.eff.org/)

11. `static` configuration, to let Nginx serve static files directly (save time, computational power, etc.) you need to add your user to `www-data` and change owner of the directory:
```
sudo usermod -a -G ec2-user www-data
sudo chown -R :www-data  /home/ec2-user/diagnosticator-server-AWS/diagnosticator-AWS/app/static
```
please note: alternatively you can move the static folder to `/var/www/` but be sure to keep it synced with the `$APP_DIR/app/static` folder in future updates. You need to point this folder to Nginx through `alias` inside `location /static` block in `diagnosticator.conf`.


---

## Updates

Whenever we (or you) make changes to the GitHub repository, to update your application accordingly:
```
cd $APP_DIR
git pull
sudo systemctl restart diagnosticator
```

---

## Development

Whenever you have a change you made that you wish to share with the whole community to possibly incorporate it in [Diagnosticator](https://diagnosticator.com):
```
cd $APP_DIR
git branch <your-name>-development
git checkout <your-name>-development
git add .
git commit -m "<your-name>-development ..."
git push https://github.com/cccnrc/diagnosticator-AWS.git <your-name>-development
```
change `<your-name>` in the above commands with your [GitHub](https://github.com/) username or whatever identifier you wish to have
