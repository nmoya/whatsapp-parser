from datetime import datetime
import re
import glob
import os
import os.path

def main(filename):

    #filename = "C:/Python27/AndroidWhatsappChats/30_BN_CF.txt"
    newpath = r'C:/Python27/AndroidWhatsappChats/parsed' 
    if not os.path.exists(newpath): os.makedirs(newpath)

    fo = open(os.path.join(newpath, filename[-12:]), "wb") #create a new file with the same name   
    with open(filename, 'rb') as f: #open the file
        #next(f) #strip the header
        for line in f:
            if line.find('ROOT') == -1 and line.find('CONTACT') == -1:
                print "corrupt line"
                continue
            index = [x.start() for x in re.finditer('-', line)]
            chatTimeString = line[0:index[0]-1]   
            print chatTimeString     
            try:
                chatTime = datetime.strptime(chatTimeString, "%b %d, %Y, %H:%M")
            except:
                chatTime = datetime.strptime(chatTimeString, "%b %d, %H:%M")    
            #print chatTime.strftime('IT format %d/%m/%y %H:%M:%S')        
            chatStringOut = chatTime.strftime('%m/%d/%y, %I:%M:%S %p')
            print chatTime.strftime(chatStringOut)
                    
            fo.write(chatStringOut + ":" + line[index[0]+1: ]) #index[0+2]      
            fo.write('\n')        
    
    fo.close()


filenameFB = glob.glob('C:/Python27/AndroidWhatsappChats/*.txt') #read in all the chat files in the directory        
for eachFile in filenameFB:    
    main(eachFile) #run the analysis for each file