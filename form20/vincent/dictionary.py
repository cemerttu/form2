
ian = {
    "Firstname":"ian",
    "lastname":"Kenyaga",
    "age":20
}
g= ian["Firstname"]
f= ian["lastname"]
b= ian["age"]

print("Firstname:", g)
print("lastname:", f)
print("age:", b)

def function(name):
    print(F"What is your name sir {name}.")

function(name="Vincent")

print("-----------------------------------------------------------------------------------------")

majid = dict(name = "ian", car = "Nissan", plain = "Boddy", school = "talanta_college")
print(dir(majid))

print(majid.items())

v = majid.values()
print(v)

f = majid.items()
print(f)

print(majid.pop("name"))

print(majid)
