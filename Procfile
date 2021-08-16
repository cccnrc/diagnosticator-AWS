web: flask db init; flask fb migrate; flask db upgrade; flask translate compile; gunicorn main:app
worker: rq worker diagnosticator-tasks
