from information_listing import show_information_menu
from vm_management import show_vm_menu
from volume_management import show_volume_menu


def show_main_menu():
    while True:
        choice = input("\n1. Listing of information\n2. Virtual machine management\n3. Volume management\n4. Exit\n")

        if choice == "1":
            show_information_menu()
        elif choice == "2":
            show_vm_menu()
        elif choice == "3":
            show_volume_menu()
        elif choice == "4":
            break
        else:
            print("Please input a valid option (1 - 4)\n")
