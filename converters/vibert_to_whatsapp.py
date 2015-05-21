import csv
from datetime import datetime
import re
import glob

def main(filename):
    

    fo = open(filename.replace("csv","txt"), "wb")    
    #    with open('C:/Python27/FBchats/9_AA_SAH.csv', 'rb') as f: #open the file
    with open(filename, 'rb') as f: #open the file
        # files don't have a header [next(f)] #strip the header
        reader = csv.reader(f) #read as csv object
        for row in reader:
            #print row
            txtLine = '\t'.join(row) #convert to a string dilineated with tab to match viber
            if txtLine.find('ROOT') == -1 and txtLine.find('CONTACT') == -1:
            #    print "corrupt line"
            #    print txtLine
               continue
            #print txtLine
            index = [x.start() for x in re.finditer('\t', txtLine)]
            chatTimeString = txtLine[0:index[1]]
            chatTimeString = re.sub('\t',' ', chatTimeString)
            #print chatTimeString

            #viber format: 20/12/2014	4:42:28 PM	CONTACT	Im next to it
            chatTime = datetime.strptime(chatTimeString, "%d/%m/%Y %H:%M:%S %p")               
            chatStringOut = chatTime.strftime('%m/%d/%y, %I:%M:%S %p')
            print chatTime.strftime(chatStringOut)
            
            tempLine = chatStringOut + ":" + txtLine[index[1]:index[2]]+":"+txtLine[index[2]:]+"\n"
            tempLine = re.sub('\t',' ', tempLine)
            fo.write(tempLine)        
    
    fo.close()

   
filenameFB = glob.glob('C:/Python27/ViberChats/*.csv') #read in all the chat files in the directory        
for eachFile in filenameFB:    
    main(eachFile) #run the analysis for each file
    print("***********")
    print eachFile
