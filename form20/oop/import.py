# print('-------import_datetime--------')
# import datetime

# now = datetime.datetime.now()
# print(now)

# print('--------import_random_number-----------')
# import random

# x = random.randint(1, 10)
# print(x)

# print('----------import_math---------')
import math

# v = math.sqrt(9)
# print(v)

# ian = math.pow(2,3)
# print(ian)


# import ceil method is work is to round up a number into the nearest integer.

# majid = math.ceil(2.6)
# Antony = math.ceil(2.6)

# print(majid)
# print(Antony)

print("-------score-------------")

number = int(input("Enter your number: "))

def ian(score):
    # print(f"You score number is {number}")
    if score >= 90:
        print("A")
    elif score >= 80:
        print("B")
    elif score >= 70:
        print("C")
    elif score >= 60:
        print("D")
    else:
        print("F")

ian(number)

