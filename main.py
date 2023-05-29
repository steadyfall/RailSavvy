'''
-------------------------------------------------
    ____        _ _______                        
   / __ \____ _(_) / ___/____ __   ___   ____  __
  / /_/ / __ `/ / /\__ \/ __ `/ | / / | / / / / /
 / _, _/ /_/ / / /___/ / /_/ /| |/ /| |/ / /_/ / 
/_/ |_|\__,_/_/_//____/\__,_/ |___/ |___/\__, /  
                                        /____/   
-------------------------------------------------

Created by Himank Dave.
'''

import sqlite3 as sqlClient
import random
from typing import Union

truthy = lambda x: True
conn = sqlClient.connect('projectTrain.db')
cur = conn.cursor()

def int_input(givenName: str, condition) -> int:
    '''
    Template for taking input for taking integers.
    '''
    number: Union[None, int] = None
    while True:
        try:
            number = int(input(givenName))
        except ValueError:
            print("The input given is not allowed.")
        else:
            if condition(number):
                break
            print("This input is not accepted.")
    return number

def str_input(givenName: str, condition) -> str:
    '''
    Template for taking input for taking strings.
    '''
    string: Union[None, str] = None
    while True:
        try:
            string = input(givenName)
        except ValueError:
            print("The input given is not allowed.")
        else:
            if condition(string):
                break
            print("This input is not accepted.")
    return string

def railsmenu():
    while True: 
        print("""| * * * Railway Reservation * * * |
|---------------------------------|
| 1. Train Detail                 |
| 2. Reservation of Ticket        |
| 3. Cancellation of Ticket       |
| 4. Display PNR                  |
| 5. Quit                         |
|---------------------------------|\n""")
        n: int = int_input("| Enter your choice : ", lambda x: True if 1 <= x <= 5 else False)
        print()
        if n == 1:
            train_detail()
        elif n == 2:
            reservation()
        elif n == 3:
            cancel()
        elif n == 4:
            displayPNR()
        else:
            return "You have successfully exit from the program!"

def train_detail():
    start: str = str_input("Enter your starting point : ", truthy)
    end: str = str_input("Enter your destination : ", truthy)
    print()

    search_command: str = f'select * from train_detail where starting_point="{start}" and (destination="{end}" or via="{end}");'
    cur.execute(search_command)
    result: list = cur.fetchall()

    if len(result) == 0:
        print("We could not find a train with given route.\n")
    else:
        for j in range(0,len(result)):
            print(f"> Information for train number - ({j+1}) :")
            print(f"| Train ID           : {result[j][0]}")
            print(f"| Cost               : {result[j][1]}")
            print(f"| Starting Point     : {result[j][2]}")
            print(f"| Destination        : {result[j][3]}")
            print(f"| VIA                : {result[j][4]}")
            print(f"| Time of Departure  : {result[j][5]}")
            print(f"| Status             : {result[j][6]}\n")
    print("===================================================================\n")

def reservation():
    status_dict: dict = {'1 SEAT LEFT!':'UNAVAILABLE', 'FILLING FAST':'1 SEAT LEFT!'}
    # Creating a unique user id
    cur.execute("select unique_id from user_information;")
    result: list = cur.fetchall()
    uid_collection: set = {x for i in result for x in i}
    uid: int = random.randint(100001,999998)
    ref: int = int(uid)
    if uid in uid_collection:
        while uid == ref:
            uid = random.randint(100001,999998)
    # Information input time!
    print("1. Enter your information as follows:")
    name: str = str_input("Enter passenger's name : ", truthy)
    age: int = int_input("Enter your age : ", lambda x: 1 <= x <= 120)
    gender: str = str_input("Enter your gender (Male / Female) : ", \
                       lambda x: True if x.upper() == 'M' or x.upper() == 'F' else False).upper()
    trainNumber: int = 0
    flag: int = 0
    while flag == 0:
        # Getting a valid train number
        trainNumber = int_input("Enter train_no : ", lambda x: True if 1_000_000 <= x <= 9_999_999 else False)
        availability_command = f'select starting_point,destination,status from train_detail where train_no={trainNumber};'
        cur.execute(availability_command)
        result: list = cur.fetchall()
        if len(result) == 0:
            print("Enter a valid train number!")
        else:
            flag = 1
    availability_command: str = f'select starting_point,destination,via,status from train_detail where train_no={trainNumber};'
    cur.execute(availability_command)
    result: list = cur.fetchall()
    start, end, via, status = result[0]
    if status == 'UNAVAILABLE':
        print(f"The train from {start} to {end} via {via} is FULLY BOOKED.")
    else:
        print(f"Starting Point : {start}")
        print(f"Destination    : {via}/{end}")
        print(" . . . . . . . .")
        add_user_command: str = f'insert into user_information (unique_id, uname, age, gender, train_no, starting_point, destination) values ({uid}, "{name}", {age}, "{gender}", {trainNumber}, "{start}", "{end}");'
        cur.execute(add_user_command)
        print(f"Information added!\n")
        cost_command: str = f'select cost from train_detail where train_no={trainNumber};'
        cur.execute(cost_command)
        result: list = cur.fetchall()
        cost: int = result[0][0]
        print(f'-> You have to pay: Rs. {cost}')
        answer: str = str_input('<< Would you like to pay the same and confirm your seat? (Y/N) : ', \
                           lambda x: x.upper() == 'Y' or x.upper() == 'N').upper()
        reserved_status: str = "NOT RESERVED"
        if answer == 'Y':
            print("\n < < Your ticket is reserved (or) confirmed! > >")
            print(f" ---> In case of cancellation your unique ID is : {uid}")
            reserved_status = "RESERVED - BOOKED"
        else:
            print(" > ! Your ticket is NOT reserved! ! <")
        reserved_status_command: str = f'update user_information set reservation="{reserved_status}" where unique_id={uid};'
        cur.execute(reserved_status_command)
        conn.commit()
        if status != 'AVAILABLE':
            updated_train_status: str = status_dict[status]
            updated_train_status_command: str = f'update train_detail set status="{updated_train_status}" where train_no={trainNumber};'
            cur.execute(updated_train_status_command)
            conn.commit()
    print("\n===================================================================\n")

def cancel():
    uid: Union[None, int] = None
    answer: Union[None, str] = None
    answer2: Union[None, str] = None
    flag: int = 0
    while flag == 0:
        # Getting a valid unique ID
        uid = int_input("Enter value of given unique ID for ticket : ", lambda x: True if 100001 <= x <= 999998 else False)
        uid_check_command = f'select * from user_information where unique_id={uid};'
        cur.execute(uid_check_command)
        result: list = cur.fetchall()
        if len(result) == 0:
            print("Enter a valid unique ID!")
        else:
            flag = 1
    answer = str_input('<< Would you like to pay the same and confirm your seat? (Y/N) : ', \
                           lambda x: x.upper() == 'Y' or x.upper() == 'N').upper()
    answer2 = str_input('<< Would you like to pay the same and confirm your seat? (Y/N) : ', \
                           lambda x: x.upper() == 'Y' or x.upper() == 'N').upper()
    if answer == 'Y' and answer2 == 'Y':
        unreserve_command: str = f'update user_information set reservation="NOT RESERVED" where unique_id={uid};'
        cur.execute(unreserve_command)
        conn.commit()
        print("\nYOUR TICKET IS CANCELLED")
    print("\n===================================================================\n")

def displayPNR():
    uid: Union[None, int] = None
    flag: int = 0
    while flag == 0:
        # Getting a valid unique ID
        uid = int_input("Enter value of given unique ID for ticket : ", lambda x: True if 100001 <= x <= 999998 else False)
        uid_check_command: str = f'select * from user_information where unique_id={uid};'
        cur.execute(uid_check_command)
        result: list = cur.fetchall()
        if len(result) == 0:
            print("Enter a valid unique ID!")
        else:
            flag = 1
    pnr_details_command: str = f'select * from user_information where unique_id={uid};'
    cur.execute(pnr_details_command)
    pnr_details: list = cur.fetchall()[0]
    cur.execute(f'select via from train_detail where train_no={pnr_details[4]}')
    via: str = cur.fetchall()[0][0]
    print(f"\n> Your current reservation status is as follows :")
    print(f"| Unique ID           : {pnr_details[0]}")
    print(f"| Passenger Name      : {pnr_details[1]}")
    print(f"| Age                 : {pnr_details[2]}")
    print(f"| Gender              : {pnr_details[3]}")
    print(f"| Train ID            : {pnr_details[4]}")
    print(f"| Starting Point      : {pnr_details[5]}")
    print(f"| Destination         : {via}/{pnr_details[6]}")
    print(f"| Reservation Status  : {pnr_details[7]}")
    print("\n===================================================================\n")

print(railsmenu())

conn.commit()
conn.close()  