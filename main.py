from sys import exit
from random import randint
from math import ceil
import sqlite3
from os import path


class Card:
    def __init__(self, _id, number, pin):
        self.id = _id
        self.number = number
        self.pin = pin
        self.balance = 0


def show_main():
    while True:
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')

        option = int(input())
        if option == 0:
            print('Bye!')
            exit()
        elif option == 1:
            card = create_card()
            insert_into_database(card)
            print('Your card has been created')
            print('Your card number:')
            print(card.number)
            print('Your card PIN:')
            print(card.pin)
        elif option == 2:
            print('Enter your card number:')
            number = input()
            print('Enter your PIN:')
            pin = input()
            result = auth_card(number, pin)

            if result is None:
                print('Wrong card number or PIN!')
            else:
                print('You have successfully logged in!')
                show_account_interactions(result)


def show_account_interactions(target: Card):
    while True:
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')

        option = int(input())

        if option == 0:
            print('Bye!')
            exit()
        elif option == 1:
            print(f'Balance: {target.balance}')
        elif option == 2:
            print('Enter income:')
            income = int(input())
            target.balance += income
            save_card(target)
        elif option == 3:
            print('Transfer')
            print('Enter card number:')
            other_num = input()

            if target.number != other_num:
                if check_checksum(other_num):
                    if not is_available(other_num):
                        print('Enter how much money you want to transfer:')
                        amount = int(input())

                        if target.balance >= amount:
                            other_card = find_card(other_num)
                            other_card.balance += amount
                            target.balance -= amount

                            save_card(other_card)
                            save_card(target)
                        else:
                            print('Not enough money!')
                    else:
                        print('Such a card does not exist.')
                else:
                    print('Probably you made a mistake in the card number. Please try again!')
            else:
                print("You can't transfer money to the same account!")
        elif option == 4:
            delete_from_database(target)
            print('The account has been closed!')
        elif option == 5:
            save_card(target)
            print('You have successfully logged out!')
            break


def rand_pin():
    return str(randint(0, 9999)).zfill(4)


def create_card():
    c_number = '400000' + get_available_number()
    c_number += get_checksum(c_number)
    c_pin = rand_pin()
    card = Card(get_id(), c_number, c_pin)
    return card


def get_available_number():
    while True:
        number = str(randint(0, 999999999)).zfill(9)
        if is_available(number):
            return number


def is_available(num: str):
    cursor.execute('SELECT number '
                   'FROM card '
                   f'WHERE number = "{num}";')
    result = cursor.fetchone()
    return result is None


def get_checksum(num: str):
    current_sum = apply_luhn_formula(num)
    return str(ceil(current_sum / 10) * 10 - current_sum)


def check_checksum(num: str):
    result = apply_luhn_formula(num[:len(num) - 1])
    return (result + int(num[len(num) - 1])) % 10 == 0


def apply_luhn_formula(num: str):
    digits: list[int] = []
    for index, s in enumerate(num):
        n = int(s)
        if index % 2 == 0:
            n *= 2
        if n > 9:
            n -= 9
        digits.append(n)
    return sum(digits)


def find_card(number: str):
    cursor.execute('SELECT * '
                   'FROM card '
                   'WHERE '
                   f'number = "{number}";')
    info = cursor.fetchone()

    if info is None:
        return None
    return Card(info[0], info[1], info[2])


def auth_card(number: str, pin: str):
    c = find_card(number)
    if c is None or c.pin != pin:
        return None
    else:
        return c


def create_database():
    if not path.exists(database_path):
        open(database_path, 'w').close()
        creating_conn = sqlite3.connect(database_path)
        creating_cursor = creating_conn.cursor()
        creating_cursor.execute('CREATE TABLE card ( '
                                'id INTEGER, '
                                'number TEXT, '
                                'pin TEXT, '
                                'balance INTEGER DEFAULT 0);')
        creating_conn.commit()


def insert_into_database(obj: Card):
    cursor.execute('INSERT INTO card (id, number, pin, balance) '
                   f'VALUES ({obj.id}, "{obj.number}", "{obj.pin}", {obj.balance});')
    conn.commit()


def delete_from_database(obj: Card):
    cursor.execute('DELETE FROM card '
                   f'WHERE number = "{obj.number}"')
    conn.commit()


def get_id():
    cursor.execute('SELECT COUNT(*) as count '
                   'FROM card;')
    n = cursor.fetchone()
    return n[0]


def save_card(obj: Card):
    delete_from_database(obj)
    insert_into_database(obj)


# cards: list[Card] = []
database_path = 'card.s3db'
create_database()
conn = sqlite3.connect(database_path)
cursor = conn.cursor()
is_available('meu')
show_main()
