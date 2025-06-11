# import math
# firstname = input("Enter your firstname: ")
# lastname = input("Enter your lastname: ")
# age = input("Ente your age: ")

# class Vincent:
#     def __init__(self, firstname, lastname, age):
#         self.first = firstname
#         self.last = lastname
#         self.age = age
#     def result(self):
#         return f"My name is {firstname} , lastname is {lastname} and age {age}"
# majid = Vincent(firstname, lastname, age)
# print(majid.result())



# print("-------function_loop--------")

# age = int(input("Enter your age: "))  # Convert to int

# def ian(age):
#     if age >= 90:
#         return "A"
#     elif age >= 80:
#         return "B"
#     elif age >= 70:
#         return "C"
#     elif age >= 60:
#         return "D"
#     else:
#         return "F"

# print("Your grade is:", ian(age))


# print("---------Dictionary_loop-------")


# contacts = {
#     "Vincent": {
#         "Phone_number": "868_594_684"
#     },
#     "Majid": {
#         "Phone_number": "868_854_954"
#     },
#     "Ryan": {
#         "Phone_number": "775_584_584_395"
#     }
# }

# def search_contact(name):
#     name = name.title()  # Make sure the name has the correct casing
#     if name in contacts:
#         return f"{name}'s Phone Number: {contacts[name]['Phone_number']}"
#     else:
#         return "Contact not found"

# # Example usage
# print(search_contact("vincent"))  # Output: Vincent's Phone Number: 868_594_684


# cat = {
#     "number": {
#         "iankenyaga":959399,
#         "Ryanmwangi":757838
#     },
#     "Age":{
#         "iankenyaga":20,
#         "Ryanmwangi":23
#     },
#     "School":{
#         "iankenyaga":"Cat_college",
#         "Ryanmwangi":"Talanta_college"
#     }
# }


# print(cat["number"]["iankenyaga"])
# print(cat["Age"]["Ryanmwangi"])
# print(cat["School"]["iankenyaga"])

# print("-------------------------------------------------------------------")


# name = input("Enter your name: ")
# age = int(input("Enter your age: "))

# class Vincent:
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#     def result(self):
#        print(f"Your name is {self.name} and {self.age}")

#     def fullname(self):
#         if (self.name) == (self.age):
#             print("I got your name and age.")
#         else:
#             print("Wrong in pass name and age.")

# majid = Vincent(name,age)
# # print(majid)
# majid.fullname()



import random
from main import start_process
# import os


# Start the game
num = random.randint(1, 10)
print("🎯 Welcome to the Guessing Game!")
# print(num)  # For debugging, leave commented out

guesses = 0
guess_list = []

# Main guessing loop
while guesses < 3:
    try:
        guess = int(input("🔢 Guess a number between 1 and 10: "))
    except ValueError:
        print("❌ Please enter a valid number.")
        continue

    guesses += 1
    guess_list.append(guess)

    if guess < num:
        print("📈 Too low! Try a higher number.")
    elif guess > num:
        print("📉 Too high! Try a lower number.")
    else:
        print(f"🎉 Good job! You guessed it in {guesses} guess(es).")
        break
else:
    print("💔 You're out of guesses.")
    print("😞 You lost.")
    # Offer one bonus guess if user remembers their first guess



    def bounce():
        try:
            memory_guess = int(input("🧠 Remember your FIRST guess? Enter it to get a bonus try: "))
        except ValueError:
            print("That's not a number. No bonus chance.")
            return

        if memory_guess == guess_list[0]:
            try:
                extra_guess = int(input("✅ Correct memory! Take one more guess: "))
            except ValueError:
                print("Invalid number. Bonus lost.")
                return

            if extra_guess == num:
                print("🎉 Wow! You nailed it with your bonus guess!")
            else:
                print(f"❌ Nope. The correct number was {num}.")
        else:
            print("❌ Wrong memory. No bonus chance.")
    bounce()


# After the guessing part, collect user info 
print("\n📝 Let's get to know you,again.")
name = str(input("Enter your name: "))
age = int(input("Enter your age: "))


# Function to validate with external process
def function(name, age):
    if start_process.firstname == name and age == start_process.age:
        print("⚠️ Registration conflict. Please try again.")
        return True
    else:
        print("✅ Info accepted. Welcome!")
        return False

# Repeat until valid registration
while True:
    if start_process():
        break
    else:
        print("\n🔃 Restarting the process. Please sign up again.")

# Final message
print(f"\n👋 Thank you {name}, age {age}. Welcome to our branch!")


            


