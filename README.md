# Postgres Multi Tenacy Manager - pgmanager
pgmanager was built on top of fabric. Also is based on the guide [Shared Postgres Hosting](https://wiki.postgresql.org/wiki/Shared_Database_Hosting)

## Features:
* Revoke default permissions from public schema
* Create database + main user
* Create an aditional user to a database
* Remove an aditional user
* Remove database + main user

## Install

### Dependences
Before install pgmanager, is need install the lastest version of postgres-client.

### Install
Install pgmanager globally using this command

    pip install -e git://github.com/nielsonsantana/postgres-multi-tenancy-manager.git#egg=pgmanager

## Configure

In order to configure pgmanager, there two options: create a file `.env` or using environment variables.

Create a file named `.env` and put the databases environments:

    DATABASE_URL_LOCAL="postgresql://<username>:<password>@127.0.0.1:5432"
    DATABASE_URL_STAGING="postgresql://<username>:<password>@127.0.0.1:5432"

Using environment variables:

    export DATABASE_URL_LOCAL="postgresql://<username>:<password>@127.0.0.1:5432"
    export DATABASE_URL_STAGING="postgresql://<username>:<password>@127.0.0.1:5432"

Then, copy the file `pgmanager_fabfile.example.py` on same directory of `.env` and start define the database environments.

    from decouple import config
    from pgmanager import *
    from pgmanager import db_environ
    from pgmanager import env

    @db_environ
    def local():
        """ DATABASE LOCAL """
        env.database_url = config('DATABASE_URL_LOCAL', '')
        env.db_super_users = ['postgres']
        env.environment = 'local'


## Usage

### Revoke Default Permissions

    pgmanager <environment> revoke_default_permissions

### Create database + main user

    pgmanager <environment> create_db_user
    
### Create aditional user for a database

    pgmanager <environment> create_extra_user

### Remove aditional user

    pgmanager <environment> remove_extra_user

### Remove database + main user

    pgmanager <environment> remove_db_user
    
### Dump database
options: binary

    pgmanager <environment> <options> dump:<database>,<dump-name>

### Restore database
options: binary

    pgmanager <environment> <options> restore:<database>,<path-dump-db>
