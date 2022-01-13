Dev Environment Setup Guide
========================

This guide covers the basic steps needed to produce a functional development environment. The default configuration supports the development environment out of the box, such that minimal configuration is required outside of the installation steps. For a more detailed deployment guide, see the [Production Environment Setup Guide](INSTALL_PROD.md).

## Dependencies

You will need Python 3 and a few additional modules to get started. For SCSS compilation you will also need NodeJS and npm.

### Debian

Tested on Debian 10.

```bash
apt install build-essential python3 python3-venv python3-pip nodejs npm
```

### Arch

```bash
pacman -S base-devel python3 python-pip nodejs npm
```

## Setup Environment

The following sequence of commands sets up and activates a python virtual environment:

```bash
mkdir sixtyfour
python3 -m venv sixtyfour
cd sixtyfour
source bin/activate
```

The name of the virtualenv will appear to the left of your shell prompt whenever it is active. When running any of the python code or pip commands related to this project, make sure your shell has the virtualenv activated. The remainder of this guide assumes the environment is active. Continue by cloning the repo and installing Python and Javascript dependencies:

```bash
git clone 'https://.../.../sixtyfour.git' src
cd src
pip3 install wheel
pip3 install -r requirements.txt
npm install
npm install -g npx
```

Verify that npx is reachable from the shell:

```bash
which npx
```

If the above fails, you should add the global node bin directory to your PATH. To lookup the global node bin directory, use:

``` bash
npm bin -g
```

## Local Settings

Create the file `sixtyfour/local_settings.py` to override settings from `sixtyfour/settings.py`:

```python
SITE_NAME = 'site name here'
SITE_LOGO = '/static/path/to/logo'

SECRET_KEY = '...a sufficiently long and secure secret key...'
```

This file is ignored by git and has a couple of uses. Primarily it is used for settings unique to your environment, such as database, secrets, and branding. It can also be used to test settings values without modifying the defaults during development.

Note: Permanent additional settings or changes to defaults of existing settings should always be made to `sixtyfour/settings.py`, as the local overrides are not tracked in source code.

## Databases

The default sqlite should be sufficient for basic development, but you may wish to upgrade to a fully-featured database.

Configure the database in `sixtyfour/local_settings.py`. Reference the following sections in the Django documentation:
https://docs.djangoproject.com/en/3.0/ref/settings/#databases
https://docs.djangoproject.com/en/3.0/ref/databases/

Each DB (aside from the default sqlite) will require additional dependencies. Only postgres dependencies will be detailed below.

### Postgres

Make sure you have the database client library installed, with the appropriate development files:
- Debian: `libpq-dev`
- Arch: `postgresql-libs`

Then, while the virtualenv is active, install following:

```bash
pip3 install psycopg2
```

## Init Database

Once database and other local settings have been configured, it is time to initialize the database. Run the following from the source directory:

```bash
./manage.py migrate
```

If the database was configured correctly you should receive OK on each migration. Go ahead and create a superuser for yourself:

```bash
./manage.py createsuperuser
```

You can use this account to access the site admin.

## Final Test

Try running the development server using the following command:

```bash
./manage.py runserver
```

Log in with your superuser account and verify that the basic functionality is working.
