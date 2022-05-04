from keystoneauth1.exceptions import ConnectFailure
from openstack.cloud import OpenStackCloudException, OpenStackCloudTimeout

from connection import ConnectionSingleton
from tabulate import tabulate
from utilities import *
from datetime import datetime


#
# VIRTUAL MACHINE MANAGEMENT
#


def create_vm():
    try:
        connection = ConnectionSingleton.get_connection()

        # Gets the name for the server (validates that the name is not empty, as this would throw an exception)
        while True:
            server_name = input("Input name of server: ").strip()

            if len(server_name) > 0:
                break
            else:
                print("\nInvalid name (must be longer than 0 characters)")

        # Gets the image the user wants to use for the instance
        print("\nAvailable images;\n")

        image_options = []

        i = 1
        for image in connection.list_images():
            print(f"[{i}] {image['name']} ({image['id']}) - Size: "
                  f"{image['size']} bytes ({round(int(image['size']) / 1073741824, 2)}GB)")
            image_options.append(image['id'])
            i += 1

        chosen_image = handle_errors("Choose image to use: ", check_int, int, "int", validate=True,
                                     validate_range=(1, i - 1))

        image_id = image_options[chosen_image - 1]
        image_size = connection.get_image(image_id)["size"]

        # Gets the flavour the user wants to use (validates that the flavour is big enough for the selected image)
        print("\nAvailable flavours;\n")

        flavour_options = []

        i = 1
        for flavour in connection.list_flavors():
            if (flavour["disk"] * 1073741824) > image_size:
                print(f"[{i}] {flavour['name']} (Disk: {flavour['disk']}GB, RAM: {flavour['ram']}MB, "
                      f"vCPUs: {flavour['vcpus']})")
                flavour_options.append(flavour['id'])
                i += 1

        chosen_flavour = handle_errors("Choose flavour to use: ", check_int, int, "int", validate=True,
                                       validate_range=(1, i - 1))

        flavour_id = flavour_options[chosen_flavour - 1]

        # Gets the key-pair the user wants to use for the instance
        print("\nAvailable key-pairs;\n")

        keypair_options = []

        i = 1
        for keypair in connection.list_keypairs():
            print(f"[{i}] {keypair['name']} ({keypair['type']})")
            keypair_options.append(keypair['name'])
            i += 1

        chosen_keypair = handle_errors("Choose keypair to use: ", check_int, int, "int", validate=True,
                                       validate_range=(1, i - 1))

        keypair_name = keypair_options[chosen_keypair - 1]

        # Gets the security group the user wants to use for the instance
        print("\nAvailable security groups;\n")

        security_options = []

        i = 1
        for security_group in connection.list_security_groups():
            print(f"[{i}] {security_group['name']} ({security_group['id']})")
            security_options.append(security_group['name'])
            i += 1

        chosen_security_group = handle_errors("Choose security group to use: ", check_int, int, "int", validate=True,
                                              validate_range=(1, i - 1))

        security_group_name = security_options[chosen_security_group - 1]

        # Creates the server
        server = connection.create_server(name=server_name, image=image_id, flavor=flavour_id,
                                          key_name=keypair_name, availability_zone="nova",
                                          security_groups=[security_group_name])

        # Displays the attributes of the created server
        print("\nCreated server;\n")

        table = [["Name", server["name"]], ["Image Name", f'{connection.get_image(server["image"]["id"])["name"]}'],
                 ["Flavour", connection.get_flavor(server['flavor']['id'])["name"]], ["Key Name", server["key_name"]]]

        print(tabulate(table, headers=["Field", "Value"], tablefmt="psql"))
    except OpenStackCloudTimeout:
        print("Request timed out")
    except OpenStackCloudException:
        print("An unknown error occurred")
    except ConnectFailure:
        print("Lost internet connection")


def shut_down():
    try:
        connection = ConnectionSingleton.get_connection()

        # Gets the server the user wants to stop (shows only servers which are currently running)
        print("Running servers (VM instances);\n")

        options = []

        i = 1
        for server in connection.list_servers():
            if server['power_state'] == 1:
                print(f"[{i}] {server['name']} ({server['id']})")
                options.append(server['id'])
                i += 1

        chosen_server = handle_errors("Choose server to shut down: ", check_int, int, "int", validate=True,
                                      validate_range=(1, i - 1))

        id_to_shutdown = options[chosen_server - 1]

        # Shuts down the server
        connection.compute.stop_server(id_to_shutdown)
    except OpenStackCloudTimeout:
        print("Request timed out")
    except OpenStackCloudException:
        print("An unknown error occurred")
    except ConnectFailure:
        print("Lost internet connection")


def remove_vm():
    try:
        connection = ConnectionSingleton.get_connection()

        # Gets the server which the user wants to deletee
        print("\nAvailable servers (VM instances);\n")

        options = []

        i = 1
        for server in connection.list_servers():
            print(f"[{i}] {server['name']} ({server['id']})")
            options.append(server['id'])
            i += 1

        chosen_server = handle_errors("Choose server to delete: ", check_int, int, "int", validate=True,
                                      validate_range=(1, i - 1))

        id_to_delete = options[chosen_server - 1]

        # Gets confirmation
        while True:
            confirmation = input("Are you sure you want to delete this server (Y/N)? ")

            if check_yes_no(confirmation):
                if confirmation.lower() == "n":
                    return
                else:
                    break
            else:
                print("\nInvalid input - please input y or n")

        # Requests the deletion of the instance
        connection.delete_server(name_or_id=id_to_delete, wait=True)
    except OpenStackCloudTimeout:
        print("Request timed out")
    except OpenStackCloudException:
        print("An unknown error occurred")
    except ConnectFailure:
        print("Lost internet connection")


def clone_vm():
    try:
        connection = ConnectionSingleton.get_connection()

        # Gets the server the user wants to clone (filters out only servers that are running
        # - servers in the build state throw an exception)
        print("Running servers (VM instances);\n")

        options = []

        i = 1
        for server in connection.list_servers():
            if server['power_state'] == 1:
                print(f"[{i}] {server['name']} ({server['id']})")
                options.append(server['id'])
                i += 1

        chosen_server = handle_errors("Choose server to clone: ", check_int, int, "int", validate=True,
                                      validate_range=(1, i - 1))

        id_to_clone = options[chosen_server - 1]

        server_to_clone = connection.get_server(id_to_clone)
        image = connection.compute.create_server_image(name=f"{server_to_clone['name']}-{datetime.now()}-image",
                                                       server=id_to_clone, wait=True, timeout=180)

        # Creates server, copying attributes from the chosen server and appending "clone" to the name
        server = connection.create_server(name=f"{server_to_clone['name']} clone",
                                          image=image["id"],
                                          flavor=server_to_clone['flavor']['original_name'],
                                          key_name=server_to_clone['key_name'],
                                          availability_zone="nova",
                                          security_groups=server_to_clone["security_groups"][0]["name"])

        # Displays attributes of the cloned server
        print("\nCreated clone server;\n")

        table = [["Name", server["name"]], ["Image Name", f'{connection.get_image(server["image"]["id"])["name"]}'],
                 ["Flavour", connection.get_flavor(server['flavor']['id'])["name"]], ["Key Name", server["key_name"]]]

        print(tabulate(table, headers=["Field", "Value"], tablefmt="psql"))
    except OpenStackCloudTimeout:
        print("Request timed out")
    except OpenStackCloudException:
        print("An unknown error occurred")
    except ConnectFailure:
        print("Lost internet connection")


def show_vm_menu():
    while True:
        choice = input("\n1. Create VM\n2. Shut down VM\n3. Remove VM\n"
                       "4. Clone VM\n5. Back\n")

        if choice == "1":
            create_vm()
        elif choice == "2":
            shut_down()
        elif choice == "3":
            remove_vm()
        elif choice == "4":
            clone_vm()
        elif choice == "5":
            break
        else:
            print("Please input a valid option (1 - 5)\n")
