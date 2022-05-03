import sys

from menu import show_main_menu
from connection import ConnectionSingleton

# if len(sys.argv) < 2:
#     print("OpenStack CLI password required as argument")
#     exit()

connection = ConnectionSingleton()
show_main_menu()
