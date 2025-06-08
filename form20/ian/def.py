# # # # # class Cow:
# # # # #     # def __init__(g,name,height):
# # # # #     #     g.n = name
# # # # #     #     g.h = height

# # # # #     def run():
# # # # #         print("Running")
    
# # # # # # cow1 = Cow("day", 45)
# # # # # # cow2 = Cow("mer", 100)
# # # # # # cow3 = Cow("ger", 130)

# # # # # # print(cow1.run())
# # # # # # print(cow2)
# # # # # # print(cow3)



# # # # # class Person:
# # # # #     def __init__(self, last, first, c1):
# # # # #         self.first = first
# # # # #         self.last = last
# # # # #         self.c1 = c1

# # # # #     def salam(self):
# # # # #         print(f"Hello {self.first} {self.last} Iam {self.c1}")

# # # # # class Child:
# # # # #     def __init__(self, first, last):
# # # # #         self.last = last
# # # # #         self.first = first

        

# # # # #     def crying(self):
# # # # #         print(f"Hi, Iam {self.first} {self.last} and i like crying.")

# # # # # c1 = Child("Vincen","samuel")
# # # # # p1 = Person("John", "Garang", c1)

# # # # # p1.salam()
# # # # # c1.crying()


# # # # # p2 = Person("Ian", "kenyaga")
# # # # # p3 = Person("Ryan", "Mwangi")
# # # # # p1.salam()
# # # # # p2.salam()
# # # # # p3.salam()
     



# # # # # cow1.name = "day"
# # # # # cow1.height = 45

# # # # # cow2.name = "mer"
# # # # # cow2.height = 100

# # # # # cow3.name = "ger"
# # # # # cow3.height = 130

# # # # print("----student_class------")


# # # # class Student:
# # # #     def __init__(self,first,last):
# # # #         self.first = first
# # # #         self.last = last
# # # #         self.email = self.last + self.first + "@" + "gmail.com"

# # # #     def get_fullname(self):
# # # #         return '{} {}'.format(self.first,self.last)
    
# # # #     def get_email(self):
# # # #         return f"{self.last}\'s email is {self.email}"
    
# # # # student1 = Student(last = "cliser", first = "John" )
# # # # student2 = Student(last = "muthiora", first = "ian" )

# # # # print(student1.get_fullname())


# # # # print("-------------------------------------------------")
# # # #create a class car with two attributes color and mileage
# # # #result
# # # #!. The blue car has 20000 miles
# # # #2. The red car has 30000 miles
# # # # class Car:
# # # #     def __init__(self,color,mileage,age):
# # # #         self.color = color
# # # #         self.mileage = mileage
# # # #         self.age = age

# # # #     def __str__(self):
# # # #         return f"The {self.color} car as the age of the car is {self.age} and {self.mileage} mileage."
    
# # # # car1 = Car(color="blue", mileage = 20000, age = 20)
# # # # car2 = Car(color="red", mileage = 30000, age = 23)

# # # # print(car1)
# # # # print(car2)


# # # # print("-----------------------exes_def_function---------")

# # # # firstname = input("Enter your firstname: ")
# # # # lastname = input("Enter your lastname: ")
# # # # age = int(input("Enter your age: "))

# # # # class Leah:
# # # #     def __init__(self, firstname, lastname, age):
# # # #         self.first = firstname
# # # #         self.last = lastname
# # # #         self.age = age
# # # #     def result(self):
# # # #         print(f"My name is {self.first} {self.last} and iam {self.age} year old.")
# # # # class Ryan():
# # # #     def Welcome():
# # # #         print("You are quite Welcome to our branch.")

# # # # name = Leah(firstname, lastname, age)
# # # # name.result()

# # # # if age >= 20:
# # # #     print(f" At {age} Years old, Go to the red door Thank you for your time.")
# # # # elif age <= 20:
# # # #     print(f"At {age} Years old, Go to the blue door Thank you for your time.")

# # # # Ryan.Welcome()

# # # # print("--------------------------------------------------------------------------------------")

# # # # firstname = input("Enter your firstname: ")
# # # # lastname = input("Enter your lastname: ")
# # # # age = int(input("Enter your age: "))

# # # # class Eva:
# # # #     def __init__(self, firstname, lastname, age):
# # # #         self.first1 = firstname
# # # #         self.last1 = lastname
# # # #         self.age1 = age
# # # #     def full_name():
# # # #          print(f"Our name is {firstname} {lastname} and age {age} years old.")
    
# # # # name = Eva(firstname, lastname, age)
# # # # name.full_name()

# # # # print("----------------------------------------------------------------")

# # # # ian = {
# # # #     "fruits":{
# # # #         "mango":"red",
# # # #         "Orange":"Orange",
# # # #     },
# # # #     "People":{
# # # #         "vincent":"Samuel",
# # # #         "ian":"kenyaga",
# # # #         "Ryan":"Mwangi"
# # # #     }
# # # # }

# # # # class Majid:
# # # #     def __init__(self, fruits, People):
# # # #         self.fruits = fruits
# # # #         self.person = People
# # # #     def result():
# # # #         print(f"What is your name")

# # # # print(["fruits"],["mango"])

# # # # print("----------------------------------------------------")
# # # firstname = input("Enter your firstname: ")
# # # lastname = input("Enter your lastname: ")
# # # age = int(input("age: "))


# # # class vincent:
# # #     def __init__(self, firstname ,lastname ,age):
# # #         self.first = firstname
# # #         self.last = lastname
# # #         self.age = age
# # #     def result(self):
# # #         print(f"Welcome {self.first}, You are the one handsome in this world!.")
# # #         print(f"I belief that lastname is {self.last} correct and age {self.age} good.")

# # # if age <= 20:
# # #     print("You are to young. Go to the red door.")
# # # elif age >= 20:
# # #     print("You are to old. Go to the blue door.")

# # # majid = vincent(firstname, lastname, age)
# # # majid.result()


# # # class Ian:
# # #     def __init__(self, name, age, ID_number):
# # #         self.name = name
# # #         self.age = age
# # #         self.ID_number = ID_number
# # #     def result(self):
# # #         print(f"You name is {self.name} , age {self.age} and ID_number {self.ID_number}")
# # #     def fullname(self):
# # #         return f""
# # # ryan = Ian(name = "Vincent", age=20, ID_number=39384212)
# # # ryan.result()

# # # class Sma:
# # #     def __init__(self,firstname, lastname, age ):
# # #         self.first = firstname
# # #         self.last = lastname
# # #         self.age = age
# # #     def result(self):
# # #         print(f"Our name is {self.first}, {self.last} and age is {self.age}")

# # # majid = Sma(firstname = "ian", lastname = "Muthiora", age = 20)
# # # majid.result()


# # ian = not(10 >= 20)

# # print(ian)

# # print(10 is not 20)

# # x = [1, 2, 3]
# # y = [1, 2, 3]
# # z = x

# # print(x is z)




# # Get user input
# firstname = input("Enter your first name: ")
# lastname = input("Enter your last name: ")
# age = int(input("Enter your age: "))

# # Define a proper class
# class Person:
#     def __init__(self, firstname, lastname, age):
#         self.first = firstname
#         self.last = lastname
#         self.age = age

#     def result(self):
#         print(f"I think your name is {self.first} {self.last} and your age is {self.age}.")

# # Age-based door assignment
# if age >= 20:
#     print("You are too old, go to the red door.")
# else:
#     print("You are too young, go to the blue door.")

# # Create instance and display info
# person = Person(firstname, lastname, age)
# person.result()

# print("-------------- Confirmation -------------")

# # Get confirmation from user
# print("\nCan you write your name and age again?")
# entered_name = input("Write your name: ")
# entered_age = int(input("Write your age: "))

# # Match checks
# if entered_name == firstname and entered_age == age:
#     print("I got your name and age.")
# else:
#     if entered_name != firstname:
#         print("This is not the correct name.")
#     if entered_age != age:
#         print("This is not the correct age.")
#     print("I did not get the correct name and age. Can you please sign in again?")

# # Final evaluation
# def evaluate_result(name, age):
#     if name == firstname and age == age:
#         print("You have passed the test. You will get the document next Monday.")
#     else:
#         print("You have failed the test. The retake will be from 01/09 to 07/09 at 8:00 AM at the Kilimani branch.")

# evaluate_result(entered_name, entered_age)





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
    entered_name = input("Write your name: ")
    entered_age = int(input("Write your age: "))

    # Define the evaluation function with restart logic
    def evaluate_result(name, age_input):
        if name == firstname and age_input == age:
            print("You have passed the test. You will get the document next Monday.")
            return True
        else:
            print("You have failed the test. The retake will be from 01/09 to 07/09 at 8:00 AM at the Kilimani branch.")
            return False

    # Return the result of evaluation
    return evaluate_result(entered_name, entered_age)

# 🔁 Main loop to restart if wrong
while True:
    if start_process():
        break  # Exit loop if correct info is provided
    else:
        print("\nRestarting the process... Please enter your information again.\n")

