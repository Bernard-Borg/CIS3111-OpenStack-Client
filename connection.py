from openstack import connect, enable_logging
import sys


class ConnectionSingleton:
    def __init__(self):
        ConnectionSingleton.__connection = None

    @staticmethod
    def get_connection():
        if ConnectionSingleton.__connection is None:
            # enable_logging(debug=True)
            ConnectionSingleton.__connection = connect(cloud="CHI-220964")

        return ConnectionSingleton.__connection
