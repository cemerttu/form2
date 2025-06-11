# number = 4
# name = "samuel"
# print(type(number))
# print(type(name))
# print(name.upper())
# number.

# class Person:
#     pass
# # # print(type(Person))
# # person1 = Person("ian")
# # person2 = Person("cliff")
# # print(person1)
# # print(person2)


# class Person:
#     def __init__(self, name):
#         self.name = name

#     def __repr__(self):
#         return f"Person({self.name}')"

# person1 = Person("ian")
# person2 = Person("cliff")

# print(person1)
# print(person2)


# print("------------------------------------------------------")



# def add(x, y):
#     return x + y

# print(add(10, 5))


# add = lambda x, y: x + y
# print(add(12, 4))

# print("---------else_if_statement--------")
# f = 20
# e = 12

# if f > e:
#     str = "Hello World!"
#     print(str)

# print("-------def_function-----------")

# firstname = input("Enter your firstname: ")
# lastname = input("Enter your lastname: ")
# age = int(input("Enter your age: "))

# class Vincent:
#     def __init__(self, firstname, lastname, age):
#         self.first = firstname
#         self.last = lastname
#         self.age = age
#     def result(self):
#         print(f"OK, you are not arrest but i need your form to know you starting with your firstname, lastname and age {self.first}, lastname {self.last} and age {self.age}")

# if age >= 20:
#     print("You are to old to play, please close the game.")
# elif age <= 20:
#     print("You are to young to play this game, There are for adult.plaese close the game")

# majid = Vincent(firstname, lastname, age)
# majid.result()


# ian = {
#     "firstname":"ian",
#     "lastname":"Muthiora",
#     "age":20
# }

# h= ian["firstname"]
# f= ian["lastname"]
# g= ian["age"]


# print("firstname", h)
# print("lastname", f)
# print("age", g)

print("----------------------------------------------------")

# import random
# import math
# class Vincent:
#     def __init__(self, SMA, EMA):
#         self.SMA1 = SMA
#         self.EMA1 = EMA

#     def crossover(self):
#         if self.EMA1 < self.SMA1:
#             print("sell")
#         elif self.EMA1 < self.SMA1:
#             print("Buy")


# samuela = random.random(Vincent)



# john = Vincent(EMA = 20, SMA=23)
# jonh = Vincent(SMA=23, EMA=20)

# john.crossover()

print("------------def_function-----------------------")

# import exes

# Get user input
def start_process():
    # Get original user input
    firstname = input("Enter your first name: ")
    lastname = input("Enter your last name: ")
    age = int(input("Enter your age: "))

    # Define a class to hold user info
    class Person:
        def __init__(self, firstname, lastname, age):
            self.first = firstname
            self.last = lastname
            self.age = age

        def result(self):
            print(f"I think your name is {self.first} {self.last} and your age is {self.age}.")

    # Age-based door assignment
    if age >= 20:
        print("You are too old, go to the red door.")
    else:
        print("You are too young, go to the blue door.")

    # Create and show result
    person = Person(firstname, lastname, age)
    person.result()

    print("-------------- Confirmation -------------")

    # Ask user to re-enter info
    print("\nCan you write your name and age again?")
    name = input("Write your name: ")
    age2 = int(input("Write your age: "))

    # Define the evaluation function with restart logic
    def evaluate_result(name, age):
        if name == firstname and age2 == age:
            print("You have failed the test. The retake will be from 01/09 to 07/09 at 8:00 AM at the Kilimani branch.")
            return True
        else:
            print("You have passed the test. You will get the document next day.")
            return False

    # Return the result of evaluation
    return evaluate_result(name, age2)

# 🔁 Main loop to restart if wrong
while True:
    if start_process():
        break  # Exit loop if correct info is provided
    else:
        print("\nRestarting the process... Please enter your information again.\n")





# print("--------------------------------------------------------------")

# print(f"You are most welcome to {firstname}")




# try:
#     a = "Hello World!"
#     print(a)
# except:
#     print("An Erro occurred.")
# finally:
#     print("Hello, Iam still printed.")



# import json

# x = {
#     "first_name":"John",
#     "last_name":"Doe",
#     "age":20
# }
# my_json = json.dumps(x)
# print(my_json)



# import re



# print("--------------------re.search()------------------")




# regex = "hello"
# txt = "hello world!"

# res = re.search(regex, txt)
# print("Index of the start and end position:", res.span())
# print("Index of the start position:", res.start())
# print("Index of the end position:", res.end())


# # Samuel = "iankenyaga"
# # John = "Ryanmwangi"

# # res = re.search(Samuel, John)
# # print("This is the start and end:", res.span())
# # print("This is start:", res.start())
# # print("This is end:", res.end())

# print("---------------re.findall()-------------------------------")
# #This method return a list that contains the vincent found

# ian = "python"
# ryan = "I love Python, because python is fun to learn!"

# vincent = re.findall(ian, ryan)
# print(vincent)


# print("-------------re.sub()----------------")
# #This methd replaces the vincent found in a string.
# # regex - the regular expression pattern
# # repl - the string replacement
# # string - the string to replace 

# njoki = "I love Python, because Python is fun to learn!"
# res = re.sub("Python", "javascript", njoki)

# print(res)

# print("----------metacharacters-----------")




