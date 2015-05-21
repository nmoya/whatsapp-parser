import csv
from datetime import datetime
import re
import glob
import os
import os.path


def main(filename):
    
#filename = 'C:/Python27/SMSchats/8_AA_LEEZ.csv'
    print filename
    fo = open(filename.replace("csv","txt"), "wb")    
    with open(filename, 'rb') as f: #open the file
        next(f) #strip the header
        reader = csv.reader(f) #read as csv object
        for row in reader:
            txtLine = ': '.join(row) #convert to a string dilineated with :
            if txtLine.find('ROOT') == -1 and txtLine.find('CONTACT') == -1:
                print "corrupt line"
                continue
            index = [x.start() for x in re.finditer(':', txtLine)]
            #print txtLine
            #print index
            chatTimeString = txtLine[0:index[3]] #find the colon ending the time string
            #print chatTimeString
            #change the formatting here
            chatTime = datetime.strptime(chatTimeString, "%m/%d/%Y: %H:%M:%S")
            #print chatTime
            #####print chatTime.strftime('IT format %d/%m/%y %H:%M:%S')        
            chatStringOut = chatTime.strftime('%m/%d/%y, %I:%M:%S %p')
            #print (chatStringOut)
                    
            #print (chatStringOut + ":" + txtLine[index[3]+1:]        )
            fo.write(chatStringOut + ":" + txtLine[index[3]+1:])        
            fo.write('\n')        
    
    fo.close()

   
filenameSMS = glob.glob('C:/Python27/SMSchats/*.csv') #read in all the chat files in the directory        
for eachFile in filenameSMS:    
    main(eachFile) #run the analysis for each file
