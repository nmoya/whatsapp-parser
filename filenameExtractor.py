import glob   

filenameTXT = glob.glob('C:/Python27/MasterChats/*.txt.json') #read in all the chat files in the directory

fo = open("C:/Python27/filenamesMaster.txt", "wb")

for f in filenameTXT:    
    print f[24:]
    fo.write('"'+f[24:]+'",\n')        
fo.close()


#print len('C:/Python27/MasterChats')
