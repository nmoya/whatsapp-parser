import csv
from datetime import datetime
import re
import glob

def main(filename):
    

    fo = open(filename.replace("csv","txt"), "wb")    
    #    with open('C:/Python27/FBchats/9_AA_SAH.csv', 'rb') as f: #open the file
    with open(filename, 'rb') as f: #open the file
        next(f) #strip the header
        reader = csv.reader(f) #read as csv object
        for row in reader:
            txtLine = ': '.join(row) #convert to a string dilineated with :
            chatTimeString = txtLine[0:19]
            #change the formatting here
            chatTime = datetime.strptime(chatTimeString, "%Y.%m.%d %H:%M:%S")
            #print chatTime.strftime('IT format %d/%m/%y %H:%M:%S')        
            chatStringOut = chatTime.strftime('%m/%d/%y, %I:%M:%S %p')
            print chatTime.strftime(chatStringOut)
                    
            fo.write(chatStringOut + ":" + txtLine[24:])        
            fo.write('\n')        
    
    fo.close()

   
filenameFB = glob.glob('C:/Python27/FBchats/*.csv') #read in all the chat files in the directory        
for eachFile in filenameFB:    
    main(eachFile) #run the analysis for each file
