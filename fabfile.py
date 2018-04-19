import dj_database_url
import getpass

from decouple import config
from fabric.api import *
from fabric.api import local as run_local
from fabric.api import env


# BASED in https://wiki.postgresql.org/wiki/Shared_Database_Hosting

# DEFAULT SETTINGS
env.grant_on_super_user = False
env.extra_dump = ''
env.extra_restore = ''

# ENVIRONMENTS


@task
def local():
    """ DATABASE LOCAL """
    env.database_url = config('DATABASE_URL_LOCAL', '')
    env.db_super_users = ['postgres']
    env.environment = 'local'


@task
def staging():
    """ DATABASE STAGING """
    env.database_url = config('DATABASE_URL_STAGING', '')
    env.db_super_users = ['genomika']
    env.environment = 'staging'
    env.grant_on_super_user = True


@task
def staging_do():
    """ DATABASE STAGING """
    env.database_url = config('DATABASE_URL_STAGING_DIGITALOCEAN', '')
    env.db_super_users = ['parceiro']
    env.environment = 'staging'


@task
def production():
    """ DATABASE PRODUCTION """
    env.database_url = config('DATABASE_URL_PRODUCTION', '')
    env.db_super_users = ['genomika']
    env.environment = 'production'


# TASKS

def run_psql(command):

    tmp_command = command.replace('    ', '')

    pqsl_command = ['psql']
    pqsl_command.append(env.database_url)
    pqsl_command.append('-c " %s "' % tmp_command)

    output = run_local(' '.join(pqsl_command))

    return output


def run_psql_direct(command):

    pqsl_command = ['psql']
    pqsl_command.append(env.database_url)
    pqsl_command.append(command)

    output = run_local(' '.join(pqsl_command))

    return output


def run_pgdump(command):

    pqsl_command = ['pgdump']
    pqsl_command.append(env.database_url)
    pqsl_command.append(command)

    output = run_local(' '.join(pqsl_command))

    return output


@task
def show_env():
    print(env)


@task
def setup_database():
    """Should be runned once per Postgres Server"""
    msg_warnning = """
    This command should be executed only one time for postgres server.
    \n y - continue \n n - abort \n\n>"""

    output = raw_input(msg_warnning)
    if output.lower() != 'y':
        return

    command = ['\nREVOKE ALL ON DATABASE template1 FROM public;']
    command.append('REVOKE ALL ON SCHEMA public FROM public;')

    for super_user in env.db_super_users:
        command.append("GRANT ALL ON SCHEMA public TO %s;" % super_user)

    run_psql('\n'.join(command))


@task
def test_select():
    run_psql("select 1;")


@task
def create_db_user(user=None, database=None, password=None):

    user = raw_input('Username: \n>')
    env.db_main_user = user
    password = getpass.getpass('Password:\n> ')
    env.db_main_user_pass = password
    database = raw_input('Database Name \n>')
    env.db_name = database

    command = ["""
    CREATE ROLE %(db_name)s NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOLOGIN;
    CREATE ROLE %(db_main_user)s NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT
    LOGIN ENCRYPTED PASSWORD '%(db_main_user_pass)s';
    GRANT %(db_name)s TO %(db_main_user)s;
    """ % env]

    for super_user in env.db_super_users:
        env.db_super_user = super_user
        if env.grant_on_super_user:
            command.append("\nGRANT %(db_main_user)s TO %(db_super_user)s;" % env)
            command.append("\nGRANT %(db_name)s TO %(db_super_user)s;" % env)

    command = ''.join(command)
    run_psql(command)

    command2 = "CREATE DATABASE %(db_name)s WITH OWNER=%(db_main_user)s;" % env
    run_psql(command2)

    command3 = "REVOKE ALL ON DATABASE %(db_name)s FROM public;" % env
    run_psql(command3)


@task
def create_extra_user(user=None, database=None, password=None):

    user = raw_input('Username: \n>')
    env.db_main_user = user
    password = getpass.getpass('Password:\n> ')
    env.db_main_user_pass = password
    database = raw_input('Database Name \n>')
    env.db_name = database

    command = """
    CREATE ROLE %(db_extra_user)s NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT
    LOGIN ENCRYPTED PASSWORD '%(db_extra_user_pass)s';
    GRANT USAGE ON SCHEMA public TO %(db_extra_user)s;
    GRANT CONNECT, TEMPORARY ON DATABASE %(db_name)s TO %(db_extra_user)s;
    GRANT %(db_name)s TO %(db_extra_user)s;""" % env

    run_psql(command)


@task
def remove_extra_user(user=None, database=None, password=None):

    extra_user = raw_input('Type extra username \n>')
    env.db_extra_user = user

    main_user = raw_input('Type main username \n>')
    env.db_main_user = main_user

    msg = 'Confirm delete %s: \n y - continue; \n n - abort \n>' % extra_user
    output = raw_input(msg)
    if output.lower() != 'y':
        return

    command = """
    -- REMOVE ALL PERMISSIONS FROM ALL OBJECTS OWNED BY DBEXTRAUSER
    -- TERMINATE CONNECTIONS OF DBEXTRAUSER
    REASSIGN OWNED BY %(db_extra_user)s TO %(db_main_user)s;
    DROP ROLE %(db_extra_user)s""" % env

    run_psql(command)


@task
def remove_db_user(user=None, database=None):

    user = raw_input('Username: \n>')
    env.db_main_user = user
    database = raw_input('Database Name: \n>')
    env.db_name = database

    command = """
    -- TERMINATE CONNECTIONS OF ALL USERS CONNECTED TO <DBNAME>
    DROP DATABASE %(db_name)s;""" % env
    run_psql(command)

    command2 = """
    DROP ROLE %(db_main_user)s;
    DROP ROLE %(db_name)s""" % env
    run_psql(command2)


@task
def restore(database=None, dump_path=None):

    user = raw_input('Username Owner Database: \n>')
    env.db_main_user = user

    if not database:
        database = raw_input('Database: \n>')
    env.db_name = database
    if not dump_path:
        dump_path = raw_input('Dump path: \n>')
    env.path = dump_path

    db_info = dj_database_url.parse(env.database_url)
    db_info['NAME'] = database

    restore_command = ['pg_restore']
    restore_command.append('-U %(db_main_user)s' % env)
    if db_info.get('NAME', ''):
        restore_command.append('-d %(NAME)s' % db_info)
    restore_command.append('-h %(HOST)s' % db_info)
    restore_command.append('-p %(PORT)s' % db_info)
    if hasattr(env, 'extra_restore'):
        restore_command.append(env.extra_restore)
    restore_command.append(' < ' + env.path)

    cmd = ' '.join(restore_command)
    run_local(cmd)


@task
def dump(database=None, dump_path=None):

    if not database:
        database = raw_input('Database: \n>')
    env.db_name = database
    if not dump_path:
        dump_path = raw_input('Dump path: \n>')
    env.path = dump_path

    cmd = 'pg_dump %(database_url)s/%(db_name)s %(extra_dump)s > %(path)s'\
        % env

    run_local(cmd)


@task
def dumpall(dump_path=None):

    command = ' < %s ' % dump_path
    run_psql_direct(command)


@task
def restoreall(database=None, dump_path=None):
    pass


@task
def binary(dump_path=None):
    env.extra_dump = '-Fc '
    env.extra_restore = '-Fc '
    env.dump_binary = True
