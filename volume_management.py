from keystoneauth1.exceptions import ConnectFailure
from openstack.cloud import OpenStackCloudTimeout, OpenStackCloudException
from connection import ConnectionSingleton
from tabulate import tabulate
from utilities import *

#
# VOLUME MANAGEMENT
#


def create_volume():
    try:
        connection = ConnectionSingleton.get_connection()

        # Get inputs
        volume_name = input("Input name of volume: ").strip()
        description = input("Input volume description: ").strip()
        size = handle_errors("Input volume size in GiB: ", check_int, int, "int", validate=True,
                             validate_range=(1, False))

        # Create volume
        volume = connection.create_volume(name=volume_name, description=description, size=size, wait=True, timeout=60)

        # Output created volume fields
        print("\nCreated volume;\n")

        table = [["Name", volume["name"]], ["Description", volume["description"]], ["Size", f'{volume["size"]}GiB'],
                ["Volume Type", volume["volume_type"]], ["Is Bootable", volume["is_bootable"]]]

        print(tabulate(table, headers=["Field", "Value"], tablefmt="psql"))
    except OpenStackCloudTimeout:
        print("Volume creation timed out")
    except OpenStackCloudException:
        print("OpenStack error occurred when creating volume")
    except ConnectFailure:
        print("Lost internet connection")


def attach_volume():
    try:
        connection = ConnectionSingleton.get_connection()

        # Get volume that the user wants to attach (filters out volumes that are already attached to an instance)
        print("\nAvailable volumes;\n")

        volume_options = []

        i = 1
        for volume in connection.volume.volumes():
            property_dict = volume.to_dict()
            if property_dict['status'] == 'available':
                print(f"[{i}] {property_dict['name']} ({property_dict['id']})")
                volume_options.append(property_dict['id'])
                i += 1

        chosen_volume = handle_errors("Choose volume to attach: ", check_int, int, "int", validate=True,
                                      validate_range=(1, i - 1))

        id_to_attach = volume_options[chosen_volume - 1]
        volume = connection.get_volume(name_or_id=id_to_attach)

        # Get the server that the user wants to attach the volume to
        print("\nAvailable servers (VM instances);\n")

        server_options = []

        i = 1
        for server in connection.list_servers():
            print(f"[{i}] {server['name']} ({server['id']})")
            server_options.append(server['id'])
            i += 1

        chosen_server = handle_errors("Choose server to attach to: ", check_int, int, "int", validate=True,
                                      validate_range=(1, i - 1))

        id_of_server = server_options[chosen_server - 1]

        server = connection.get_server(name_or_id=id_of_server)

        # Attach the volume to the server
        connection.attach_volume(server=server, volume=volume)
    except OpenStackCloudTimeout:
        print("Request timed out")
    except OpenStackCloudException:
        print("An unknown error occurred")
    except ConnectFailure:
        print("Lost internet connection")


def detach_volume():
    try:
        connection = ConnectionSingleton.get_connection()

        # Get the volume which the user wants to detach (filters out volumes which are not attached)
        print("\nIn-use volumes;\n")

        volume_options = []

        i = 1
        for volume in connection.volume.volumes():
            property_dict = volume.to_dict()

            if property_dict['status'] == "in-use":
                attached_server = connection.get_server(property_dict['attachments'][0]['server_id'])
                print(f"[{i}] {property_dict['name']} ({property_dict['id']}): Attached to {attached_server['name']} "
                      f"({attached_server['id']}) at {property_dict['attachments'][0]['device']}")
                volume_options.append(property_dict['id'])
                i += 1

        chosen_volume = handle_errors("Choose volume to detach: ", check_int, int, "int", validate=True,
                                      validate_range=(1, i - 1))

        id_to_detach = volume_options[chosen_volume - 1]
        volume = connection.get_volume(name_or_id=id_to_detach)

        server = connection.get_server(name_or_id=volume['attachments'][0]["server_id"])
        print(f"Detaching volume from server {server['name']} ({server['id']})")

        connection.detach_volume(server=server, volume=volume)
    except OpenStackCloudTimeout:
        print("Request timed out")
    except OpenStackCloudException:
        print("An unknown error occurred")
    except ConnectFailure:
        print("Lost internet connection")


def remove_volume():
    try:
        connection = ConnectionSingleton.get_connection()

        # Get the volume the user wants to delete
        print("\nAvailable volumes;\n")

        options = []

        i = 1
        for volume in connection.volume.volumes():
            property_dict = volume.to_dict()
            if property_dict['status'] == "available":
                print(f"[{i}] {property_dict['name']} ({property_dict['id']})")
                options.append(property_dict['id'])
                i += 1

        chosen_volume = handle_errors("Choose volume to delete: ", check_int, int, "int", validate=True,
                                      validate_range=(1, i - 1))

        id_to_delete = options[chosen_volume - 1]

        # Gets confirmation from the user
        while True:
            confirmation = input("Are you sure you want to delete this volume (Y/N)? ")

            if check_yes_no(confirmation):
                if confirmation.lower() == "n":
                    return
                else:
                    break
            else:
                print("\nInvalid input - please input y or n")

        # Requests the deletion of the volume
        connection.delete_volume(name_or_id=id_to_delete, wait=True, timeout=60)
    except OpenStackCloudException:
        print("An unknown error occurred")
    except ConnectFailure:
        print("Lost internet connection")


def show_volume_menu():
    while True:
        choice = input("\n1. Create volume\n2. Attach volume\n3. Detach volume\n4. Remove volume\n5. Back\n")

        if choice == "1":
            create_volume()
        elif choice == "2":
            attach_volume()
        elif choice == "3":
            detach_volume()
        elif choice == "4":
            remove_volume()
        elif choice == "5":
            break
        else:
            print("Please input a valid option (1 - 5)\n")