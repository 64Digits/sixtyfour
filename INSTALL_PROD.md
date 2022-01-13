Production Environment Setup Guide
========================

Running in production is slightly more involved. In general, the concepts outlined in the [Deploying Django](https://docs.djangoproject.com/en/3.0/howto/deployment/) documentation can be applied to arrive at a stable and efficient environment.

While there is no single optimal configuration, this guide covers the basics of setting up a production server in one possible configuration. Several caveats to be aware of:
- This is just a starting point
- Your mileage may vary
- You should do more than merely what is laid out in this guide

So as usual know your situation, know your environment, and if ever in doubt go read the Django/uwsgi/nginx/etc docs.

## Getting Started

The goal is to run the Django server via uwsgi, proxy uwsgi through nginx, and serve static files through nginx. Additional configuration points will be discussed, as well as optional features and systemd units. The following general configuration is assumed:

| Property | Value |
| ---: | :--- |
| Operating System | Debian 10 |
| HTTP Server | nginx 1.14 |
| Database Server | PostgreSQL 11 |
| Primary DNS Name | sixtyfour.local |
| Media DNS Name | media-sixtyfour.local <br> (CNAME to sixtyfour.local) |
| uwsgi socket | 127.0.0.1:9090 |
| virtualenv location | /opt/sixtyfour |
| app repo location | /opt/sixtyfour/app |
| media location | /opt/sixtyfour/media |
| static location | /opt/sixtyfour/static |
| nginx root location | /var/www/sixtyfour |

Substitute these with your own configuration in mind. Commands are run as root from the app repository location. Media directories and certain files are chowned by `www-data:www-data` as noted.

This guide starts by assuming that the basic installation steps have been performed, the dev environment is working, and that an appropriate database has already been configured (See the [Dev Environment Setup Guide](INSTALL_DEV.md)).

### Dependencies

```sh
apt install nginx
```

From within the active virtualenv:

```sh
pip3 install uwsgi
```

## Configuring sixtyfour

Update the file `/opt/sixtyfour/app/sixtyfour/local_settings.py`

```python
SITE_NAME='sixtyfour'
SITE_LOGO='/static/images/logo.svg'

DEBUG = False
ALLOWED_HOSTS=['sixtyfour.local']

STATIC_ROOT='/opt/sixtyfour/static'
MEDIA_ROOT='/opt/sixtyfour/media'

MEDIA_URL='http://media-sixtyfour.local/'

SECRET_KEY = '...a sufficiently long and secure RANDOM secret key that you generate for this environment...'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[sixtyfour] '
```

Be sure the database configuration is also present. To verify the database connection is working, run the following while the virtualenv is active:

```sh
./manage.py migrate
```

Run the following commands to generate css and collect static files in the new location:
```sh
./manage.py compilescss
./manage.py collectstatic
```

## Configuring uwsgi

Create the file `/opt/sixtyfour/app/uwsgi.ini`
```ini
[uwsgi]
socket = 127.0.0.1:9090
chdir = /opt/sixtyfour/app/
wsgi-file = sixtyfour/wsgi.py
processes = 4
threads = 2
stats = 127.0.0.1:9191
virtualenv = /opt/sixtyfour
uid = www-data
gid = www-data
```

You may want to adjust the number of processes or threads according to available resources, or set additional uwsgi settings. See the [uwsgi documentation](https://uwsgi-docs.readthedocs.io/en/latest/) for details.

## Configuring systemd

Create the file `/lib/systemd/system/sixtyfour.service`

```ini
[Unit]
Description=sixtyfour via uwsgi
After=syslog.target network.target

[Service]
Type=simple
ExecStart=/opt/sixtyfour/bin/uwsgi uwsgi.ini
WorkingDirectory=/opt/sixtyfour/app
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target
```

## Configuring nginx

Only the essentials will be covered here. It would be wise to extend this configuration, for example, by enabling and enforcing HTTPS only (or permanent HTTP redirect to HTTPS), restricting content types served, configure server/client side caching, request body size restrictions, and any other security or performance related measures that may apply but are beyond the scope of this guide.

Create the file `/etc/nginx/sites-available/sixtyfour`

```nginx
server {
        listen 80;
        listen [::]:80;

        server_name sixtyfour.local;

        # WARNING: Existing files under this location will be served and such requests will not pass through to uwsgi!
        root /var/www/sixtyfour;
        # This could be useful for something like certbot that places files to be served from /.well-known
        # Could also be useful for serving a few files such as /favicon.ico, or /robots.txt

        access_log /var/log/nginx/sixtyfour.access.log;
        error_log /var/log/nginx/sixtyfour.error.log;

        location / {
                try_files $uri @uwsgi;
        }

        location @uwsgi {
                include uwsgi_params;
                # Uncomment the following line when enabling HTTPS
                #uwsgi_param UWSGI_SCHEME https;
                uwsgi_pass 127.0.0.1:9090;
        }

        location /static {
                rewrite  ^/static/(.*) /$1 break;
                root /opt/sixtyfour/static;
                try_files $uri $uri/ =404;
        }
}

server {
        listen 80;
        listen [::]:80;

        server_name media-sixtyfour.local;

        root /opt/sixtyfour/media;
        index index.html index.htm;

        location / {
                try_files $uri $uri/  =404;
        }

        access_log /var/log/nginx/sixtyfour-media.access.log;
        error_log /var/log/nginx/sixtyfour-media.error.log;
}
```

Create a symlink to activate the configuration:
```sh
ln -s /etc/nginx/sites-available/sixtyfour /etc/nginx/sites-enabled/sixtyfour
```

## Some notes on security

It is not possible to discuss every possible security measure, always refer to the relevant documentation of your tools for a much better starting point. I'll touch on just a few things briefly here.

### Internal

You might consider securing `local_settings.py` through file permissions:

```sh
chown www-data:www-data sixtyfour/local_settings.py
chmod 660 sixtyfour/local_settings.py
```

Note: There are better ways to protect the secrets in that file if you get creative. It's a python file after all! Django provides some possible ideas when discussing critical settings in their [deployment checklist](https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/).

### External

At the very least, enable a firewall on your server and only allow necessary services to be accessible publicly; ideally only HTTP/HTTPS is accessible publicly (and properly secured SSH if you rely on it).

Read the uwsgi docs to find out what can go wrong when you don't secure the uwsgi socket. On that note, a socket file with locked down permissions is not such a bad idea from an internal security standpoint as well.

You should also consider hardening your nginx configuration if you haven't already. SSL is not covered in this guide but on the public web it is a must. Look into LetsEncrypt and certbot if nothing else. To address some of the threats associated with user uploaded files, use a distinct top-level media domain and limit content types when serving uploaded content. To address some of the threats related to DoS attacks and other abuse, limit request body sizes (this is a tradeoff against max upload size).

Django covers a number of security topics in their [documentation](https://docs.djangoproject.com/en/3.0/topics/security/). Also read over their [deployment checklist](https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/) before going live!

## Testing

Once all of the configurations are in place and everything is secured to your liking, try to bring up the server:

```sh
systemctl start sixtyfour
systemctl start nginx
```

Navigate your browser to `sixtyfour.local` and verify that the site is functional. If all of your configurations agree, enable the two services so that they are started on boot:

```sh
systemctl enable sixtyfour
systemctl enable nginx
```

## Email

You should make sure that email is working properly, as it is required for registration. If you have a local smtp server installed, you may not need to do anything aside from specify the SMTP backend in your `local_settings.py`.

* [Configure email backend in Django](https://docs.djangoproject.com/en/3.0/topics/email/#smtp-backend)
* [Configure email-based error reporting in Django](https://docs.djangoproject.com/en/3.0/howto/error-reporting/#email-reports)
* [General email topics in Django](https://docs.djangoproject.com/en/3.0/topics/email/)

## Optional Features

### Geolocation

Geolocation is an optional feature of IP logging and may be provided through GeoIP2. First install the python dependency:

```sh
pip3 install geoip2
```

Geolocation data must be downloaded separetely, [in binary format](https://dev.maxmind.com/geoip/geoip2/geolite2/). Configure GeoIP2 in `local_settings.py`:

```python
GEOIP_PATH='/opt/sixtyfour/share/geolite2'
```

You can see Django's [GeoIP2 documentation](https://docs.djangoproject.com/en/3.0/ref/contrib/gis/geoip2/) for more details.

## Upgrading in place

It is recommended to use git to manage all code changes. However a git pull is not always enough to upgrade the site running in production.

Whenever you update code for the production site you should at minimum run the following commands inside the virtualenv:

```sh
./manage.py migrate
./manage.py compilescss
./manage.py collectstatic
```

Once this has been done, restart the uwsgi service:

```sh
systemctl restart sixtyfour
```

Side note: despite requiring a virtualenv, manage.py commands can still be scripted for convenience sake:
```sh
#!/bin/bash
PREFIX="/opt/sixtyfour"
cd "$PREFIX/app"
source "$PREFIX/bin/activate"
./manage.py migrate
./manage.py compilescss
./manage.py collectstatic --no-input
deactivate
```

