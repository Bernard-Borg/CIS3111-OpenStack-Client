import sys
from openstack.exceptions import SDKException
from menu import show_main_menu
from connection import ConnectionSingleton

# Confirms that the user passed in an argument
if len(sys.argv) < 2 or len(sys.argv) < 3:
    print("Selected cloud (from the cloud.yaml file) and OpenStack CLI password required as arguments")
    exit(1)

connection = ConnectionSingleton().get_connection()

# Checks that the password is correct
try:
    connection.authorize()
except SDKException as e:
    if e.message.message.startswith("Unrecognized schema"):
        print("Password provided is incorrect")
    else:
        print("Please connect to the internet")
    exit(-1)

show_main_menu()
