import datetime
import re

# Position where the first character of a name is found in each line
start = 19

# File containing the watsapp conversation
file_name = "Chat.CONTACT2-py.txt"


def get_name(line):
   end = line.find(":", start)
   return line[start:end]

def get_text(line):
   end = line.find(":", start)
   return line[end+2:len(line)]

def check_special(line):
   if ((line.find("joined") != -1) or (line.find("changed subject") != -1)):
      return 1
   else:
      return 0



a=0      
print "Processing file..."
now = datetime.datetime.now()
whatsapp = open(file_name, "r")
for line in whatsapp:
   print("enter loop")
   print(a)
   a=a+1
   if not check_special(line) and (re.search("../../.. ..:..:..:", line)):
    print("first not")
    if not os.path.exists("parserWords/"+get_name(line)):
      print("second not")
      os.makedirs("parserWords/"+get_name(line))
      file = open("parserWords/"+get_name(line)+"/"+str(now), "a")
      file.write(get_text(line))
print "Done! Go to the parserWords folder!"