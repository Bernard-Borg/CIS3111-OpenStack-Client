from openstack.exceptions import ConfigException
from openstack import connect
import sys


# Singleton class for the connection
class ConnectionSingleton:
    def __init__(self):
        ConnectionSingleton.__connection = None

    @staticmethod
    def get_connection():
        try:
            if ConnectionSingleton.__connection is None:
                ConnectionSingleton.__connection = connect(cloud=sys.argv[1], password=sys.argv[2])
        except ConfigException:
            print("\nProvided cloud name was not found (please provide the one in the clouds.yaml file) "
                  "OR the clouds.yaml file is missing\n")
            exit(-1)

        return ConnectionSingleton.__connection
