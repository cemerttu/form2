# class vincent:
#     def __init__(self,firstname, lastname,age):
#         self.firstname = firstname
#         self.lastname = lastname
#         self.age = age
#     def fullname(self):
#         print(f"Hello, My name is {self.firstname}  {self.lastname} and Iam {self.age}")

# class samuel:
#     def Welcome(self):
#         print("Welcome to cat college and our former branch was kips college.")

#     def name(self):
#         print("and our branch it also give medical if you need.")

# majid = vincent(f"ian", "Kenyaga", 23,)
# majid.fullname()

# ryan = samuel()
# ryan.Welcome()
# ryan.name()


# print("--------form_with_class/object---------")
# firstname = input("Enter your firstname: ")
# lastname = input("Enter your lastname: ")
# age = int(input("Enter your age"))

# class Ian:
#     def __init__(self, firstname, lastname,age ):
#         self.first = firstname
#         self.last = lastname
#         self.age = age
#     def result(self):
#         print(f"Our branch is Welcoming {self.first} of you to accupliaction.")
#         print(f"And i believe the lastname {self.last}. Good")
#         print(f"and your age {self.age}")
# class Vincent:
#     def Fullname(self):
#         print("")
# Majid = Ian(firstname, lastname,age)

# print("--------function_def-----")

# def function(age):
#     for i in age:
#         if age <= 20:
#             print("You are to young. go to the red door.")
#         elif age >= 20:
#             print("You are to young. go to the blue door.")
# function(age)
# Majid.result()

print("--------------------------------import_time-----------")

import datetime

c = datetime.datetime.now()

print(c)
firstname = input("Enter your firstname: ")
lastname = input("Enter your lastname: ")
age = input("Enter your age: ")

def function(firstname, lastname, age):
    print(f"I believe that the name are {firstname}, {lastname} and {age}")
function()

