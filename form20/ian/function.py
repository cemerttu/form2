# import random
# print("Welcome to guess a number")

# guess = 0
# num = random.randint(1,10)


# while guess < 3:
#     number = int(input("Guess  a number:"))
#     guess += 1
#     if number > num:
#         print(f"Sorry you choose {number} Try a lower number.")
#     if number <  num:
#         print(f"Sorry you choose {number} Try a Higher number.")
#     if number == num:
#         print("You won")
#         break    
# if number != num:
#     print("You run out of chances😡")


# def num_gues_game(number ,num = random.randint(1,10), guess = 0):
#     # print(num)
#     while guess < 3:
#         number = int(input("Guess  a number:"))
#         guess += 1
#         if number > num:
#             print(f"Sorry you choose {number}, Try a lower number.")
#         if number <  num:
#             print(f"Sorry you choose {number}, Try higher number")
#         if number == num:
#             print("You won")
#             break    
#     if number != num:
#         print("You run out of chances😡")
#         print(f"You number{num}")

# num_gues_game(2)




import subprocess

data = subprocess.check_output(['netsh','wlan','show','profiles']).decode('utf-8').split('\n')

profiles = [i.split(":")[1].strip() for i in data if "All User Profile" in i]

for i in profiles:
    results = subprocess.check_output(['netsh','wlan','show','profile', i, 'key=clear']).decode('utf-8').split('\n')
    results = [b.split(":")[1].strip() for b in results if "Key Content" in b]

    try:
        print("{:<30}| {:<}".format(i, results[0]))
    except IndexError:
        print("{:<30}| {:<}".format(i, ""))






