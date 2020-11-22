import random
import sqlite3
import sys


def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def create_table(_conn):
    cur = _conn.cursor()
    cur.execute('DROP TABLE card')
    cur.executescript(''' CREATE TABLE IF NOT EXISTS card (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
            );
    ''')
    _conn.commit()


def acc_generator():
    middle_numbers = random.randint(100000000, 999999999)
    card_number = "400000" + str(middle_numbers)
    sum_of_numbers = 0
    iterator = 1
    for i in card_number:
        if iterator % 2 != 0:
            i = 2 * int(i)
            if int(i) > 9:
                i = int(i) - 9
        sum_of_numbers += int(i)
        iterator += 1
    if sum_of_numbers % 10 != 0:
        last_digit = 10 - (sum_of_numbers % 10)
    else:
        last_digit = 0
    card_number = card_number + str(last_digit)
    first_pin = str(random.choice('0123456789'))
    second_pin = str(random.choice('0123456789'))
    third_pin = str(random.choice('0123456789'))
    fourth_pin = str(random.choice('0123456789'))
    card_pin = first_pin + second_pin + third_pin + fourth_pin
    print("Your card has been created")
    print(f"Your card number:\n{card_number}")
    print(f"Your card PIN:\n{card_pin}")
    cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card_number, card_pin,))
    conn.commit()


def luhn_algorithm(card_to_check):
    luhn = True
    global scope
    global sum_to_check
    global checksum
    global luhn_error
    while luhn:
        card_iterator = 1
        sum_to_check = 0
        checksum = 0
        for i in card_to_check:
            if card_iterator < 16:
                if card_iterator % 2 != 0:
                    i = 2 * int(i)
                    if int(i) > 9:
                        i = int(i) - 9
                sum_to_check += int(i)
                card_iterator += 1
            else:
                checksum = int(i)
                break
        if card_to_check[0] != '4':
            print("Such a card does not exist.")
            luhn_error = 1
            return
        elif (sum_to_check + checksum) % 10 != 0:
            print("Probably you made a mistake in the card number. Please try again!")
            luhn_error = 1
            return
        else:
            cur.execute("""SELECT * FROM card WHERE number = ?""", (target_account,))
            global target_user
            target_user = cur.fetchone()
            if target_user is None:
                print("Such a card does not exist.")
                luhn_error = 1
                return
            elif target_account == user_card_number:
                print("You can't transfer money to the same account!")
                luhn_error = 1
                return
            else:
                amount_to_transfer = int(input("Enter how much money you want to transfer:"))
                target_balance = target_user["balance"]
                cur.execute("""SELECT balance FROM card WHERE number =? """, (user_card_number,))
                new_user_data = cur.fetchone()
                new_acc_balance = new_user_data["balance"]
                if amount_to_transfer > new_acc_balance:
                    print("Not enough money!")
                    return
                else:
                    new_acc_balance -= amount_to_transfer
                    target_balance += amount_to_transfer
                    cur.execute("""UPDATE card SET balance = ? WHERE number = ? """, (target_balance, target_account,))
                    cur.execute("""UPDATE card SET balance = ? WHERE number = ? """, (new_acc_balance, user_card_number,))
                    conn.commit()
                    print("Success!")
                    return


def do_transfer():
    global target_account
    target_account = input("Enter card number:")
    luhn_algorithm(target_account)
    if luhn_error == 1:
        return
    return


def acc_menu():
    global acc_balance
    acc_balance = current_user["balance"]
    run = True
    while run:
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")
        acc_option = input(">")
        if acc_option == "1":
            print(f"Balance: {acc_balance}")
        elif acc_option == "2":
            income = int(input("Enter income:"))
            acc_balance += income
            cur.execute(""" UPDATE card
                            SET balance = ?
                            WHERE number = ?;
            """, (acc_balance, user_card_number,))
            conn.commit()
            print("Income was added!")
            print(acc_balance)
        elif acc_option == "3":
            do_transfer()
        elif acc_option == "4":
            cur.execute("""DELETE FROM card WHERE number = ?""", (user_card_number,))
            conn.commit()
            print("The account has been closed!")
            break
        elif acc_option == "5":
            break
        elif acc_option == "0":
            conn.close()
            sys.exit()


conn = create_connection('card.s3db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
create_table(conn)

while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    code = input()
    if code == "1":
        acc_generator()
    elif code == "2":
        user_card_number = input("Enter your card number:\n")
        user_card_pin = input("Enter your PIN:\n")
        cur.execute('SELECT * from card WHERE number = ? AND pin = ?', (user_card_number, user_card_pin,))
        current_user = cur.fetchone()
        if current_user is not None:
            print("You have successfully logged in!")
            acc_menu()
        else:
            print("Wrong card number or PIN!")
        continue
    elif code == "0":
        if conn is not None:
            conn.close()
            exit()
        else:
            exit()
