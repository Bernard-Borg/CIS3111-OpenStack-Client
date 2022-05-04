from keystoneauth1.exceptions import ConnectFailure
from connection import ConnectionSingleton
from tabulate import tabulate

#
# LISTING OF INFORMATION
#


def list_available_images():
    try:
        connection = ConnectionSingleton.get_connection()

        table = []

        print("\nList of available images;\n")
        for image in connection.image.images():
            property_dict = image.to_dict()
            table.append([property_dict["id"], property_dict["name"], property_dict["status"]])

        print(tabulate(table, headers=["ID", "Name", "Status"], tablefmt="psql"))
    except ConnectFailure:
        print("Lost internet connection")


def list_stored_keypairs():
    try:
        connection = ConnectionSingleton.get_connection()

        table = []

        print("\nList of stored key-pairs;\n")
        for keypair in connection.list_keypairs():
            property_dict = keypair.to_dict()
            table.append([property_dict["name"], property_dict["fingerprint"], property_dict["type"]])

        print(tabulate(table, headers=["Name", "Fingerprint", "Type"], tablefmt="psql"))
    except ConnectFailure:
        print("Lost internet connection")


def list_available_volumes():
    try:
        connection = ConnectionSingleton.get_connection()

        table = []

        print("\nList of available volumes;\n")
        for volume in connection.volume.volumes():
            property_dict = volume.to_dict()
            table.append([property_dict["id"], property_dict["name"], property_dict["status"], property_dict["size"]])

        print(tabulate(table, headers=["ID", "Name", "Status", "Size"], tablefmt="psql"))
    except ConnectFailure:
        print("Lost internet connection")


def list_security_groups():
    try:
        connection = ConnectionSingleton.get_connection()

        table = []

        print("\nList of available security groups;\n")
        for security_group in connection.list_security_groups():
            property_dict = security_group.to_dict()
            table.append([property_dict["id"], property_dict["name"], property_dict["description"],
                          property_dict["project_id"], property_dict["tags"]])

        print(tabulate(table, headers=["ID", "Name", "Description", "Project ID", "Tags"], tablefmt="psql"))
    except ConnectFailure:
        print("Lost internet connection")


def list_available_ips():
    try:
        connection = ConnectionSingleton.get_connection()

        table = []

        print("\nList of available IP addresses;\n")
        for floating_ip in connection.list_floating_ips():
            if floating_ip["fixed_ip_address"] is None:
                table.append([floating_ip["id"], floating_ip["floating_ip_address"]])

        print(tabulate(table, headers=["ID", "IP Address"], tablefmt="psql"))
    except ConnectFailure:
        print("Lost internet connection")


def show_information_menu():
    while True:
        choice = input("\n1. List available images\n2. List stored key-pairs\n3. List available volumes\n"
                       "4. List security groups\n5. List available IPs\n6. Back\n")

        if choice == "1":
            list_available_images()
        elif choice == "2":
            list_stored_keypairs()
        elif choice == "3":
            list_available_volumes()
        elif choice == "4":
            list_security_groups()
        elif choice == "5":
            list_available_ips()
        elif choice == "6":
            break
        else:
            print("Please input a valid option (1 - 6)\n")