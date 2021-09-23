![Status](https://img.shields.io/badge/status-alpha-red)
[![Version](https://img.shields.io/docker/v/biolachs2/lab_orchestrator)](https://hub.docker.com/r/biolachs2/lab_orchestrator/tags)
[![License](https://img.shields.io/github/license/laborchestrator/laborchestrator-api)](https://github.com/LabOrchestrator/laborchestrator-api/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/laborchestrator/laborchestrator-api)](https://github.com/laborchestrator/laborchestrator-api/issues)
[![Downloads](https://img.shields.io/docker/pulls/biolachs2/lab_orchestrator)](https://hub.docker.com/r/biolachs2/lab_orchestrator)

# Lab Orchestrator API

This project contains the lab orchestrator API.

[Github](https://github.com/LabOrchestrator/LabOrchestrator-api)  
[Docker Hub](https://hub.docker.com/r/biolachs2/lab_orchestrator)

## Installation

- `docker pull biolachs2/lab_orchestrator`

or

- `git clone https://github.com/LabOrchestrator/LabOrchestrator-API.git && cd LabOrchestrator-API && pip3 install -r requirements.txt`

## Documentation

Check out the developer documentation at [laborchestrator-api.readthedocs.io](https://laborchestrator-api.readthedocs.io/en/latest/).

## Environment Variables

- `KUBERNETES_SERVICE_HOST` (str): Host of your Kubernetes API (if you run `kubectl proxy`: `localhost`). In Kubernetes this variable is set automatically.
- `KUBERNETES_SERVICE_PORT` (int): Port of your Kubernetes API (if you run `kubectl proxy`: `8001`). In Kubernetes this variable is set automatically.
- `DEVELOPMENT` (bool): If this is true the development mode is activated. This means, that no cacert is used and insecure certs are allowed. If false this assumes you are running this inside a Kubernetes cluster.
- `SECRET_KEY` (str): This key is used to create jwt tokens. Create a random key for this and keep this key safe.
- `DEBUG`: Activates the django debug mode.
- `DATABASE_ENGINE` (str): Selects the database engine to be used. Can be either `sqlite3` or `postgres`.
- `POSTGRES_DB` (str): Name of the postgres db.
- `POSTGRES_USER` (str): User of the postgres db.
- `POSTGRES_PASSWORD` (str): Password of the user.
- `POSTGRES_SERVICE_HOST` (str): Host address of the postgres db.
- `POSTGRES_SERVICE_PORT` (int): Port of the postgres db.
- `EMAIL_USE_TLS` (bool): True if TLS should be activated during connection to the mail server.
- `EMAIL_HOST` (str): Host of the mail server.
- `EMAIL_PORT` (int): Port of the mail server.
- `EMAIL_HOST_USER` (str): User of the mail server.
- `EMAIL_HOST_PASSWORD` (str): Password of the user.
- `DEFAULT_FROM_EMAIL` (str): Email address of the default sender of mail.
- `ACCOUNT_EMAIL_VERIFICATION` (str): If set to `none`, no mails are send or required. If set to `optional` a verification mail is send, but it's not required to verify mails. If set to `mandatory` a verification mail is send and it's required to verify mails.
- `ALLOWED_HOSTS` (list of str): A list of hosts that are allowed.
- `USE_X_FORWARDED_HOST` (bool): If you run this program behind a reverse proxy you should activate `X_FORWARDED_HOSTs` and set this to true. Otherwise the allowed hosts won't work.
- `LAB_VNC_HOST` (str): External host address of the LabVNC instance. Should be the domain name where you run this, for example: `laborchestrator.com`.
- `LAB_VNC_PORT` (int): Port of the LabVNC instance. Default is 30003, you should set it to 80 or 443.
- `LAB_VNC_PROTOCOL` (str): The protocol that should be used. Valid values: `http` or `https`.
- `LAB_VNC_PATH` (str): The path to the novnc html script that should be opened. For example: `labvnc/vnc_lite.html`.
- `WS_PROXY_HOST` (str): The external host address of the websocket proxy. Should be the domain name where you run this, for example: `laborchestrator.com`.
- `WS_PROXY_PORT` (int): The port of the ws proxy instance. Default is 30002, you should set it to 80 or 443.
- `DJANGO_SUPERUSER_EMAIL` (str): Only needed when you run it through docker. Email address of the admin that should be created.
- `DJANGO_SUPERUSER_PASSWORD`: Only needed when you run it through docker. Password of the admin that should be created.
- `DJANGO_SUPERUSER_FIRST_NAME`: Only needed when you run it through docker. First name of the admin that should be created.
- `AMOUNT_WORKERS`: Only needed when you run it through docker. Amount of gunicorn workers that should be started to handle requests.


## Setup

**Development**:

Set the environment variables and install the dependencies. Then you can start it with: `./manage.py runserver`.

**Production:**

When running in production you should not use the django runserver. You should use a wsgi server. Take a look at the `docker-entrypoint.sh` script.

**Configuration:**

To collect static files (which is needed in production environments) run: `python manage.py collectstatic --noinput`

To migrate the database run: `python manage.py migrate`

To create a superuser run: `python manage.py createsuperuser --no-input`

**Admin Page:**

This API contains an admin page where you can control many resources. You can open it at `youraddress.com/admin`. You should go to `Sites` and configure your domain name and display name. These values will be used in emails. It's also possible to add social logins on your own risk, but they are currently untested. Please report any error on that.

## Usage

The API contains a browsable API. The core api is available through `/api`. It contains the resources `docker_image`, `lab`, `lab_instances` and `users`.

Docker Images are links to a docker image that contains a VM. These resources can only be created by admins.

Labs are combination of docker images. You can add multiple docker images to a lab. A lab can be started by users.

If a user starts a lab a lab instance is created and all VMs that are associated to the lab are started in Kubernetes. You will get a url where you can access the VNC of the VMs. The VMs are started in a network and you can connect from one VM to another in you lab. You can't connect to VMs from other users or other labs.

Access to the VMs requires a running WebsocketProxy and a LabVNC instance. Access is done via JWT tokens. The token is part of the response when you create a lab instance. If you forget the token or want a new one you can go to the details view of the lab instance and append `/token` to the url. Example: `youraddress.com/api/lab_instances/3/token`. This will create a new token for the VMs in this lab. A token is only valid 10 minutes.

When done with your lab instance you should delete it, because it wont be deleted automatically.

In addition to the browsable API you have an openapi-schema and a swagger ui.

## Contributing

### Issues

Feel free to open [issues](https://github.com/LabOrchestrator/LabOrchestrator-API/issues).

### Developer Dependencies

- Python 3.8
- Make
- `pip install -r requirements.txt`
- `pip install -r requirements-dev.txt`

### Releases

Your part:

1. Create branch for your feature (`issue/ISSUE_ID-SHORT_DESCRIPTION`)
2. Code
3. Make sure test cases are running and add new ones for your feature
4. Create MR into master
5. Increase version number in `lab_orchestrator/__init__.py` (semantic versioning)

Admin part:

1. Check and accept MR
2. Merge MR
3. Run `make release`

### Docs

To generate the docs run: `cd docs && make html`.
