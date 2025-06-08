# # print("Welcome to Cat_college")
# # t = input("Enter your name: ")

# # class vincent:
# #     def __init__(self,t):
# #         self.t = t

# # ian = vincent(t)

# # t =ian.t

# # print("Firstname: ",)



# # x = "I love {} very much!"
# # ian = x.format("Python")

# # print(ian)

# # f = "I love {}, {} and {} very much!"
# # Vincent = f.format("Ian", "Majid", "Ryan")

# # print(Vincent)

# # john = "I love {2}, {}"






# import subprocess

# # Get all Wi-Fi profiles
# data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')

# # Extract profile names
# profiles = [line.split(":")[1].strip() for line in data if "All User Profile" in line]

# # Show passwords for each profile
# for profile in profiles:
#     try:
#         results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8', errors='ignore').split('\n')
#         password_line = [line for line in results if "Key Content" in line]
#         password = password_line[0].split(":")[1].strip() if password_line else ""
#         print("{:<30}| {:<}".format(profile, password))
#     except subprocess.CalledProcessError:
#         print("{:<30}| {:<}".format(profile, "Error retrieving password"))





import subprocess

data = subprocess.check_output(['netsh','wlan','show','profiles']).decode('utf-8').split('\n')

profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]

for i in profiles:
    try:
        results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split('\n')
        password = next((b.split(":")[1][1:-1] for b in results if "Key Content" in b), "")  # More efficient
        print(f"{i:<30}| {password:<}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving password for profile: {i} - {e}") #handle the error.


