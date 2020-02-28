import logging
import os


format = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
# DO NOT USE logging.DEBUG in prod unless you want to potentially log passwords
# logging.basicConfig(format=format, level=logging.DEBUG)
logging.basicConfig(format=format, level=logging.INFO)


def get_env(name):
    try:
        return os.environ[name]
    except KeyError as e:
        raise Exception(f"Expected environment variable {name} not set; {e}")


DEFAULT_SG = get_env('auth_ssh_from_local_sg')