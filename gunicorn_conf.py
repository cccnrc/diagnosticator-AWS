bind = ':8001'
worker_class = 'sync'
loglevel = 'debug'
accesslog = '/home/ec2-user/diagnosticator-server-AWS/diagnosticator_access.log'
acceslogformat ="%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog =  '/home/ec2-user/diagnosticator-server-AWS/diagnosticator_error.log'
