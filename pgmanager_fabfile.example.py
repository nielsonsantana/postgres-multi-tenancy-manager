
from decouple import config
from pgmanager import *
from pgmanager import db_environ
from pgmanager import env
from pgmanager import run_psql
from fabric.api import task


# ENVIRONMENTS


@db_environ
def local():
    """ DATABASE LOCAL """
    env.database_url = config('DATABASE_URL_LOCAL', '')
    env.db_super_users = ['postgres']
    env.environment = 'local'


# CUSTOM TASKS

@task
def select1():
    run_psql('select 1;')
