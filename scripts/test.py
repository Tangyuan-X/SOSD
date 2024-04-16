import os

lists = os.listdir("." + os.sep + "123")
for i in lists:
    if i.endswith('.png'):
        os.remove(os.path.join("." + os.sep + "123", i))
