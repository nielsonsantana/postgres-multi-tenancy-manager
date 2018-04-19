
from decouple import config
from fabric.api import env
from fabric.api import task
from pgmanager import *


# ENVIRONMENTS


@task
def local():
    """ DATABASE LOCAL """
    env.database_url = config('DATABASE_URL_LOCAL', '')
    env.db_super_users = ['postgres']
    env.environment = 'local'
