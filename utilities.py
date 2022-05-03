from typing import Callable, Iterable


def check_yes_no(check_str: str):
    if check_str.strip().lower() == "y" or check_str.strip().lower() == "n":
        return True
    else:
        return False


def check_int(check_str: str):
    try:
        int(check_str)
        return True
    except ValueError:
        return False


def validate_int_range(prompt: str, type_checker: Callable, type_converter: Callable, type_str: str):
    while True:
        raw_result = input(prompt).strip()

        if type_checker(raw_result):
            return type_converter(raw_result)
        else:
            print(f"\nYour input was not of type {type_str}, please try again")


def handle_errors(prompt: str, type_checker: Callable, type_converter: Callable, type_str: str,
                  validate: bool = False, validate_range: tuple = (False, False)):
    while True:
        raw_result = input(prompt).strip()

        if type_checker(raw_result):
            converted_result = type_converter(raw_result)

            if type(converted_result) == int and validate:
                if validate_range[0] is not False:
                    if converted_result < validate_range[0]:
                        print(f"\nYour input was outside the valid range (< {validate_range[0]}), please try again")
                        continue

                if validate_range[1] is not False:
                    if converted_result > validate_range[1]:
                        print(f"\nYour input was outside the valid range (> {validate_range[1]}), please try again")
                        continue

            return converted_result
        else:
            print(f"\nYour input was not of type {type_str}, please try again")
