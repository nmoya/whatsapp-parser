# -*- coding: utf-8 -*-
from __future__ import division
from datetime import datetime
import codecs
import date
import re
import operator
import sys
import json
import csv
import numpy
import matplotlib.pyplot as plt
from pprint import pprint




class Chat():

    def __init__(self, filename):
        self.filename = filename
        self.raw_messages = []

        self.datelist = []
        self.timelist = []
        self.senderlist = []
        self.messagelist = []
        self.chatTimeList = []
        self.rootResponseTimeList = []
        self.contactResponseTimeList = []
        self.rootBurstList = []
        self.contactBurstList = []
        self.rootInitiations = 0
        self.contactInitiations = 0

    def open_file(self):
        arq = codecs.open(self.filename, "r", "utf-8-sig")
        content = arq.read()
        arq.close()
        lines = content.split("\n")
        lines = [l for l in lines if len(l) != 1]
        for l in lines:
            self.raw_messages.append(l.encode("utf-8"))

    def feed_lists(self):
        for l in self.raw_messages:
            msg_date, sep, msg = l.partition(": ")
            raw_date, sep, time = msg_date.partition(" ")
            sender, sep, message = msg.partition(": ")
            #print ("\n\n\nRAW: ")
            #print (raw_date)
            raw_date = raw_date.replace(",", "")
            #print (raw_date)
            #print ("\n\n\n")
            if message:
                self.datelist.append(raw_date) 
                self.timelist.append(time) #here is the time object; save it              
                colonIndex = [x.start() for x in re.finditer(':', l)]
                #print ind
                chatTimeString = l[0:colonIndex[2]] #grab the characters that make up the date and time (Everthing until the third colon

                if "AM" in chatTimeString or "PM" in chatTimeString:
                    chatTime = datetime.strptime(chatTimeString, "%m/%d/%y, %I:%M:%S %p") #convert to a data object, format of the whatsapp data 8/2/14, 12:59:24 PM
                else:
                    chatTime = datetime.strptime(chatTimeString, "%d/%m/%y %H:%M:%S") #convert to a data object, format of the whatsapp data 8/2/14, 12:59:24 PM
                
                
#                chatTime = datetime.strptime(chatTimeString, "%m/%d/%y, %I:%M:%S %p") #convert to a data object, format of the whatsapp data 8/2/14, 12:59:24 PM
                self.chatTimeList.append(chatTime)                               
                self.senderlist.append(sender)
                self.messagelist.append(message)
            else:
                self.messagelist.append(l)
        t0=self.chatTimeList[0]
        senderIndex=0;
        burstCount=1; #variable to count the number of messages in a row sent by sender

        rootName = "ROOT"
        contactName = "CONTACT"
        INITIATION_THRESHOLD = (8*60*60)
        
        for t1 in self.chatTimeList[1:]: #perform the operations that are dependant on multiple messages (response time, bursts)
            dt = t1-t0
            if self.senderlist[senderIndex] != self.senderlist[senderIndex-1]: #is sender the same as the last message?
                #sender changed, store the burst count and reset 
#                print("sender changed: %s") %(self.senderlist[senderIndex])
                if (dt.seconds > INITIATION_THRESHOLD):
                    if self.senderlist[senderIndex] == rootName:
                        self.rootInitiations +=1
                    elif self.senderlist[senderIndex] == contactName:
                        self.contactInitiations +=1
                    else:    
                        sys.exit("ERROR CHANGE NAMES IN CHAT TO ROOT AND CONTACT1\n")                    
                #print("response time: %d\n" %(dt.seconds) )
                if self.senderlist[senderIndex] == rootName:    #is sender the root?
                    self.contactBurstList.append(burstCount) #store the burst count for the last sender, which is the opposite of current
                    self.rootResponseTimeList.append(dt.seconds)                    
                elif self.senderlist[senderIndex] == contactName: #is sender the contact?
                    self.rootBurstList.append(burstCount) #store the burst count for the last sender, which is the opposite of current
                    self.contactResponseTimeList.append(dt.seconds)
                else:   
                        errorName = self.senderlist[senderIndex]
                        sys.exit("ERROR CHANGE NAMES IN CHAT TO ROOT AND CONTACT2\n")                    
                burstCount = 1  
                
                #save 
                
            else:
                burstCount+=1 #accumulate the number of messages sent in a row  
                if burstCount >= 3:
                    print"bursting: %d %s\n" %(burstCount, self.senderlist[senderIndex])        
                #print"repeat sender: %d %s\n" %(burstCount, self.senderlist[senderIndex])
               
            
            #self.responseTimeList.append(dt.seconds)
            t0 = t1            
            senderIndex+=1
            
        
    def print_history(self, end=0):
        if end == 0:
            end = len(self.messagelist)
        for i in range(len(self.messagelist[:end])):
            print self.datelist[i], self.timelist[i],\
                self.senderlist[i], self.messagelist[i]

    def get_senders(self):
        senders_set = set(self.senderlist)
        return [e for e in senders_set]

    def count_messages_per_weekday(self):
        counter = dict()
        for i in range(len(self.datelist)):
            month, day, year = self.datelist[i].split("/") #AN edited date order
            parsed_date = "%s-%s-%s" % (year, month, day)
            #print ("DATE: ")
            #print (parsed_date)
            #print ("\n\n")
            weekday = date.date_to_weekday(parsed_date)
            if weekday not in counter:
                counter[weekday] = 1
            else:
                counter[weekday] += 1
        return counter

    def count_messages_per_shift(self):
        shifts = {
            "latenight": 0,
            "morning": 0,
            "afternoon": 0,
            "evening": 0
        }
        for i in range(len(self.timelist)):
            hour = int(self.timelist[i].split(":")[0])
            if hour >= 0 and hour <= 6:
                shifts["latenight"] += 1

            elif hour > 6 and hour <= 11:
                shifts["morning"] += 1

            elif hour > 11 and hour <= 17:
                shifts["afternoon"] += 1

            elif hour > 17 and hour <= 23:
                shifts["evening"] += 1
        return shifts

    def count_messages_pattern(self, patternlist):
        counters = dict()
        pattern_dict = dict()
        senders = self.get_senders()
        for pattern in patternlist:
            counters[pattern] = dict()
            for s in senders:
                counters[pattern][s] = 0
            pattern_dict[pattern] = re.compile(re.escape(pattern), re.I) #re=regular expression, .I = ignore case, .compile = convert to object 
        for i in range(len(self.messagelist)):
            for pattern in patternlist:
                search_result = pattern_dict[pattern].\
                    findall(self.messagelist[i])
                length = len(search_result)
                if length > 0:
                    if pattern not in counters:
                        counters[pattern][self.senderlist[i]] = length
                    else:
                        counters[pattern][self.senderlist[i]] += length
        return counters

    def print_patterns_dict(self, pattern_dict):
        for pattern in pattern_dict:
            print pattern
            for s in pattern_dict[pattern]:
                print s, ": ", pattern_dict[pattern][s]
            print ""

    def message_proportions(self):
        senders = self.get_senders()
        counter = dict()
        total = 0
        for i in ["messages", "words", "chars", "qmarks", "exclams", "media"]:
            counter[i] = dict()
            for s in senders:
                counter[i][s] = 0
        for i in range(len(self.senderlist)):
            counter["messages"][self.senderlist[i]] += 1
            counter["words"][self.senderlist[i]] += \
                len(self.messagelist[i].split(" "))
            counter["chars"][self.senderlist[i]] += len(self.messagelist[i])
            counter["qmarks"][self.senderlist[i]] += self.messagelist[i].count('?')
            counter["exclams"][self.senderlist[i]] += self.messagelist[i].count('!')
            counter["media"][self.senderlist[i]] += (
                                                    self.messagelist[i].count('<media omitted>')+
                                                    self.messagelist[i].count('<image omitted>')+
                                                    self.messagelist[i].count('<image omitted>')+
                                                    self.messagelist[i].count('<audio omitted>')+
                                                    self.messagelist[i].count('<‎immagine omessa>')+
                                                    self.messagelist[i].count('<video omesso>')+
                                                    self.messagelist[i].count('<‎vCROOTd omessa>')+
                                                    self.messagelist[i].count('Photo Message')+
                                                    self.messagelist[i].count('Video Message')+
                                                    self.messagelist[i].count('Sticker')
                                                    )
            total += 1
        counter["total_messages"] = 0
        counter["total_words"] = 0
        counter["total_chars"] = 0
        counter["total_qmarks"] = 0
        counter["total_exclams"] = 0
        counter["total_media"] = 0

        for s in senders:
            counter["total_messages"] += counter["messages"][s]
            counter["total_words"] += counter["words"][s]
            counter["total_chars"] += counter["chars"][s]
            counter["total_qmarks"] += counter["qmarks"][s]
            counter["total_exclams"] += counter["exclams"][s]
            counter["total_media"] += counter["media"][s]
        return counter

    def average_message_length(self):
        msg_prop = self.message_proportions()
        counter = dict()
        for s in self.get_senders():
            counter[s] = msg_prop["words"][s] / msg_prop["messages"][s]
        return counter

    def most_used_words(self, top=10, threshold=3):
        words = dict()
        for i in range(len(self.messagelist)):
            message_word = self.messagelist[i].split(" ")
            for w in message_word:
                if len(w) > threshold:
                    w = w.decode("utf8")
                    w = w.replace("\r", "")
                    w = w.lower()
                    if w not in words:
                        words[w] = 1
                    else:
                        words[w] += 1
        sorted_words = sorted(words.iteritems(), key=operator.itemgetter(1),
                              reverse=True)
        counter = 0
        output = sorted_words[:top]
        return output

def printDict(dic, parent, depth):
    tup = sorted(dic.iteritems(), key=operator.itemgetter(1))
    isLeaf = True
    for key in tup:
        if isinstance(dic[key[0]], dict):
            isLeaf = False
    if isLeaf and depth!=0:
        print " "*(depth-1)*2, parent
    for key in tup:
        if isinstance(dic[key[0]], dict):
            printDict(dic[key[0]], key[0], depth+1)
        else:
            print " "*depth*2, str(key[0]), "->", dic[key[0]]


def main(filenameAN):
    #if len(sys.argv) < 2:
    #    print "Run: python main.py <TextFileName> [regex. patterns]"
    #    sys.exit(1)
    #c = Chat(sys.argv[1])
    c = Chat(filenameAN)
    c.open_file()
    c.feed_lists()
    output = dict()
    RESPONSE_TIME_THRESHOLD = (3*60*60) #number hours for 'big delay' in response time (to strip out in response time calculation)
    BURST_THRESHOLD = 3 #consider a 'burst' if someone sends 3 or more messages in a row

    
    print "\n--PROPORTIONS"
    output["proportions"] = c.message_proportions()
    printDict(output["proportions"], "proportions", 0)
    
    print "\n--SHIFTS"
    output["shifts"] = c.count_messages_per_shift()
    printDict(output["shifts"], "shifts", 0)

#  WEEKDAY CAN'T HANDLE BOTH TIME FORMATS YET
#    print "\n--WEEKDAY"
 #   output["weekdays"] = c.count_messages_per_weekday()
  #  printDict(output["weekdays"], "weekday", 0)

    print "\n--AVERAGE MESSAGE LENGTH"
    output["lengths"] = c.average_message_length()
    printDict(output["lengths"], "lengths", 0)

    print "\n--PATTERNS"
    output["patterns"] = c.count_messages_pattern(sys.argv[2:])
    printDict(output["patterns"], "patterns", 0)

    print "\n--INITIATIONS"
    print("root initiations %d" %c.rootInitiations)
    print("contact initiations %d" %c.contactInitiations)
    output["rootInitiations"] = c.rootInitiations
    output["contactInitiations"] = c.contactInitiations
    try:
        initiationRatio = c.rootInitiations/c.contactInitiations
    except:
        initiationRatio = c.rootInitiations
    output["initiationRatio"] = initiationRatio
    
    print "\n--=RESPONSE TIMES"
    accumRT=0
    rtCtr = 0
    rootInitCtr = 0
    
    (hist, bin_edges) = numpy.histogram(numpy.asarray(c.rootResponseTimeList))
    plt.plot(bin_edges[0:-1], numpy.log(hist+1), ".-r")
    plt.show()
    print ("hist: %s\n" %hist)
    print ("be: %s\n" %bin_edges)
    for rt in c.rootResponseTimeList:
        if rt < RESPONSE_TIME_THRESHOLD:
            rtCtr += 1
            accumRT += rt
    print("SUM OF ROOT RT: %s, from %s messages\n" %(accumRT, rtCtr))
    rootRTavg = accumRT/rtCtr
    print("AVG OF ROOT RT: %s\n" %(rootRTavg))
       
    accumRT=0
    rtCtr = 0
    for rt in c.contactResponseTimeList:
        if rt < RESPONSE_TIME_THRESHOLD:
            rtCtr += 1
            accumRT += rt
    print("SUM OF CONTACT RT: %s, from %s messages\n" %(accumRT, rtCtr))
    contactRTavg = accumRT/rtCtr
    print("AVG OF CONTACT RT: %s\n" %(contactRTavg))
    print("RT RATIO ROOT/CONTACT: %s\n" %(rootRTavg/contactRTavg))
    
    output["rootResponseTimes"] = rootRTavg
    output["contactResponseTimes"] = contactRTavg
    output["responseTimeRatio"] = rootRTavg/contactRTavg
   

    print "\n--BURSTS"
    burstCtrRoot = 0
    accumBurstRoot = 0
    for burst in c.rootBurstList:
        if burst >= BURST_THRESHOLD:
            burstCtrRoot += 1
            accumBurstRoot += burstCtrRoot
    print("SUM OF ROOT BURSTS: %s, from %s instances\n" %(accumBurstRoot, burstCtrRoot))

    try:
        rootBurstavg = accumBurstRoot/burstCtrRoot
    except:
        rootBurstavg = 0
 
    burstCtrContact = 0
    accumBurstContact = 0
    for burst in c.contactBurstList:
        if burst >= BURST_THRESHOLD:
            burstCtrContact += 1
            accumBurstContact += burstCtrContact

    try:
        contactBurstavg = accumBurstContact/burstCtrContact
    except:
        contactBurstavg = 0            
           
    output["rootBurstNum"] = burstCtrRoot
    output["contactBurstNum"] = burstCtrContact

    try:
        output["burstNumRatio"] = burstCtrRoot/burstCtrContact    
    except:
        output["burstNumRatio"] = burstCtrRoot
    
    output["rootBurstLength"] = rootBurstavg
    output["contactBurstLength"] = contactBurstavg        
    try:
        output["burstLengthRatio"] = rootBurstavg/contactBurstavg    
    except:
        output["burstLengthRatio"] = rootBurstavg    


    
    print "\n--TOP 15 MOST USED WORDS (length >= 3)"
    output["most_used_words"] = c.most_used_words(top=15, threshold=3)
    output["most_used_words"] = sorted(output["most_used_words"], key=operator.itemgetter(1), reverse=True)
    #print output["most_used_words"]
    #for muw in output["most_used_words"]:
    #    print muw[0]

    #print "TIMESTAMPS\n %s\n\n" %c.chatTimeList[0:4]
    #print "Root Response time sample \n %s...\n" %c.rootResponseTimeList[0:4]
    #print "Contact Response time sample \n %s...\n" %c.contactResponseTimeList[0:4]
    #print "Root bursts \n %s\n" %c.rootBurstList
    #print "Contact bursts \n %s\n" %c.contactBurstList
    #print "Median response time =%s\n\n" %(numpy.median(c.responseTimeList))
    
    output["senders"] = c.get_senders()
    #nameTest = sys.argv[1] 
    arq = open(filenameAN + ".json", "w")
    arq.write(json.dumps(output))
    pprint(output)
    arq.close()
    
#basepath = "C:/Python27/MasterChats/"    

import glob   
filenameTXT = glob.glob('C:/Python27/MasterChats/*.txt') #read in all the chat files in the directory

for f in filenameTXT:    
    print f
    print ("**************")
    main(f) #run the analysis for each file

