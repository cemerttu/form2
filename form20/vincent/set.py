x = {"dog",21,True}
c = {"ian","Antony","cat_college"}
print(x)
#for_loop
for i in x:
    print(i)
#Adding items
x.add("watermelon")
print(x)
#removing items

x.remove(True)
print(x)

#check in items is present
print("dog" in x)
print("ian" in x)
#combine two sets
x.update(c)
print(x)
#Difference of two sets
print("x - c:",x - c)
print("c -x:", c - x)

