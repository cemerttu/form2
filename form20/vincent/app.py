# name = input("Enter your name: ")
# age = int(input("Enter your age: "))

# def ian(name, age):
#     print(name, age)

# if age >= 20:
#     print("You are too old. Go to the red door.")
# else:
#     print("You are too young. Go to the blue door.")

# age += 1  # Optional: if you need to increment age for some reason

# ian(name, age)



# class vincent:
#     def __init__(self,name,age):
#         self.name = name
#         self.age = age

# ian = vincent("Ian",23)

# i =ian.name
# d =ian.age

# print("-----list-------------")

# print("Firstname: ",i)
# print("lastname: ",d)

# majid = dict(car = "Nissan", house = "Finheight_apartment", school = "cat_college", )

# print(len(majid))
# print(dir(majid))


# # majid.append("airplain")
# # print(majid)


# x = majid.values()
# print(x)

print("------------------------------------------------------")
firstname = input("Enter your firstname: ")
lastname = input("Enter your lastname: ")
age = int(input("Enter your age: "))

class Vincent:
    def __init__(self, firstname, lastname, age):
        self.first = firstname
        self.last = lastname
        self.age = age
    def return2(self):
        return f"You firstname,lastname and age {self.first}, {self.last}, {self.age}."
if age >= 20:
    print("You are old.go to the red door.")
else:
    print("You are young.go to the blue door.")

form = Vincent(firstname, lastname, age)
form.return2()

name = input("Enter your name: ")
age = int(input("Enter your age: "))


def function(name, age):
    if name == firstname and name == age:
        print("I got your name and age")
    elif name != firstname:
        print("Wrong name.")
    elif age != age:
        print("Wrong age.")

function(name, age)    


