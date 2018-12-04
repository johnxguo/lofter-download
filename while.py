import os

os.system("python single.py")

def isDone():
    done = True
    for line in open("list.txt"):
        line = line.rstrip("\n")
        if line != "" and os.path.isdir(line):
            if os.path.isfile(line + "/undone"):
                print(line + " not done")
                done = False
            else:
                print(line + " done")
    return done

while 1:
    os.system("python batch.py")
    if isDone():
        break
        
print("\nall done!\n")