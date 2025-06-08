majid = ["dog","cat","rabbits","fish","hamster"]
print(majid[:2])
print(majid[1:2])


majid.append("Monkey")
print(majid)

majid.remove("cat")
print(majid)

majid.pop()
print(majid)

majid.reverse()
majid.insert(0, "rabbits")
majid.insert(2, "Mango")

majid.copy()
majid.index('dog')
print(majid)
print(len(majid))
print(dir(majid))

majid.sort()
print(majid)
