import os
for line in open("list.txt"):
    line = line.rstrip("\n")
    if line != "":
        os.system("python lofter.py " + line)