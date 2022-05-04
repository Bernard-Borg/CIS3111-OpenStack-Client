from openstack import connect
import sys


# Singleton class for the connection
class ConnectionSingleton:
    def __init__(self):
        ConnectionSingleton.__connection = None

    @staticmethod
    def get_connection():
        if ConnectionSingleton.__connection is None:
            ConnectionSingleton.__connection = connect(cloud="CHI-220964", password=sys.argv[1])

        return ConnectionSingleton.__connection
