import glob   

filenameTXT = glob.glob('C:/Python27/MasterChats/*.txt.json') #read in all the chat files in the directory

fo = open("C:/Python27/filenamesMaster.txt", "wb")

for f in filenameTXT:    
    print f
    fo.write('"'+f+'",\n')        
fo.close()


