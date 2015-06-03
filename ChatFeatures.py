# -*- coding: utf-8 -*-
from __future__ import division
import datelib
import re
import operator

class ChatFeatures():

    def __init__(self):
        self.root_response_time    = []
        self.contact_response_time = []
        self.root_burst            = []
        self.contact_burst         = []
        self.initiations           = {}
        self.weekday               = {}
        self.shifts                = {}
        self.patterns              = {}
        self.proportions           = {}
        self.most_used_words       = {}

    def compute_response_time_and_burst(self, list_of_messages, root_name, senders, initiation_thrs=(60*60*8), burst_thrs=3, response_thrs=(60*60*3)):
        # perform the operations that are dependant on multiple messages
        # (response time, bursts)
        self.initiations = {}
        for s in senders:
            self.initiations[s] = 0
        t0 = list_of_messages[0].datetime_obj
        burst_count = 1
        for index, message in enumerate(list_of_messages):
            #skip the first message since we are looking at differences; note this means we don't count first msg as init
            if index == 0:
                continue
            t1 = message.datetime_obj
            dt = t1 - t0
            dt.total_seconds()

            print "sender %s delta %s" % ( message.sender, dt.total_seconds() )
            if (dt.total_seconds() > initiation_thrs):
                self.initiations[message.sender] += 1

            # is sender the same as the last message?
            if message.sender != list_of_messages[index-1].sender:
                # sender changed, store the burst count and reset
                #print "sender changed: %s" % ( message.sender )
                #print "burst count: %s" % ( burst_count )

                #print("response time: %d\n" %(dt.total_seconds()) )
                # is sender the root?
                if message.sender == root_name:
                    # store the burst count for the last sender, which is the
                    # opposite of current
                    if burst_count > burst_thrs:
                        #print "BURST CONTACT ENDED: %s IN A ROW" % ( burst_count )
                        self.contact_burst.append(burst_count)
                    if dt.total_seconds() < response_thrs:
                        self.root_response_time.append(dt.total_seconds())
                # is sender the contact?
                else:
                    # store the burst count for the last sender, which is the
                    # opposite of current
                    if burst_count > burst_thrs:
                        #print "BURST ROOT ENDED: %s IN A ROW" % ( burst_count )
                        self.root_burst.append(burst_count)
                    if dt.total_seconds() < response_thrs:
                        self.contact_response_time.append(dt.total_seconds())
                
                # End of the first burst, restart the counter
                burst_count = 1

            else:
                # accumulate the number of messages sent in a row
                burst_count += 1
            t0 = t1
        if burst_count > burst_thrs: #catch a burst if at end of chat
            #print "final burst: %s" % ( burst_count )
            if  message.sender == root_name:
                self.root_burst.append(burst_count)
            else:
                self.contact_burst.append(burst_count)                

    def compute_messages_per_weekday(self, list_of_messages):
        self.weekday = {
            "Sunday": 0,
            "Monday": 0,
            "Tuesday": 0,
            "Wednesday": 0,
            "Thursday": 0,
            "Friday": 0,
            "Saturday": 0
        }
        for msg in list_of_messages:
            weekday = datelib.date_to_weekday(msg.date)
            if weekday not in self.weekday:
                self.weekday[weekday] = 1
            else:
                self.weekday[weekday] += 1
        return self.weekday

    def compute_messages_per_shift(self, list_of_messages):
        self.shifts = {
            "latenight": 0,
            "morning": 0,
            "afternoon": 0,
            "evening": 0
        }
        for msg in list_of_messages:
            hour = int(msg.time.split(":")[0])
            if hour >= 0 and hour <= 6:
                self.shifts["latenight"] += 1

            elif hour > 6 and hour <= 11:
                self.shifts["morning"] += 1

            elif hour > 11 and hour <= 17:
                self.shifts["afternoon"] += 1

            elif hour > 17 and hour <= 23:
                self.shifts["evening"] += 1
        return self.shifts

    def compute_messages_pattern(self, list_of_messages, senders, pattern_list):
        self.patterns = {}
        regexes = {}
        for pattern in pattern_list:
            self.patterns[pattern] = {}
            for sender in senders:
                self.patterns[pattern][sender] = 0
            # re=regular expression, .I = ignore case, .compile = convert to object
            regexes[pattern] = re.compile(re.escape(pattern), re.I)
        for msg in list_of_messages:
            for pattern in pattern_list:
                search_result = regexes[pattern].findall(msg.content)
                length = len(search_result)
                if length > 0:
                    if pattern not in self.patterns:
                        self.patterns[pattern][msg.sender] = length
                        print "This should never happen"
                    else:
                        self.patterns[pattern][msg.sender] += length
        return self.patterns

    def compute_message_proportions(self, list_of_messages, senders, root, contact):
        total = 0
        self.proportions = {}
        categories = ["messages", "words", "chars", "qmarks", "exclams", "media"]
        for i in categories:
            self.proportions[i] = {}
            for s in senders:
                self.proportions[i][s] = 0
        for msg in list_of_messages:
            self.proportions["messages"][msg.sender] += 1
            self.proportions["words"][msg.sender]    += len(msg.content.split(" "))
            self.proportions["chars"][msg.sender]    += len(msg.content.strip())
            self.proportions["qmarks"][msg.sender]   += msg.content.count('?')
            self.proportions["exclams"][msg.sender]  += msg.content.count('!')
            self.proportions["media"][msg.sender] += (
                msg.content.count('<media omitted>') +
                msg.content.count('<image omitted>') +
                msg.content.count('<image omitted>') +
                msg.content.count('<audio omitted>') +
                msg.content.count('<‎immagine omessa>') +
                msg.content.count('<video omesso>') +
                msg.content.count('<‎vCROOTd omessa>') +
                msg.content.count('Photo Message') +
                msg.content.count('Video Message') +
                msg.content.count('Sticker')
            )
            total += 1

        self.proportions["avg_words"] = {}
        for s in senders:
            self.proportions["avg_words"][s] = self.proportions["words"][s] / self.proportions["messages"][s]
        self.proportions["avg_words"]["ratio"] = self.proportions["avg_words"][root] / self.proportions["avg_words"][contact]

        for c in categories:
            self.proportions[c]["total"] = 0
            for s in senders:
                self.proportions[c]["total"] += self.proportions[c][s]
        
        for c in categories:
         
            #if a value is 0, replace with a 1 to avoid zero erros in ratio calcs.
            if self.proportions[c][contact] == 0:
                self.proportions[c][contact] = 1
            if self.proportions[c][root] == 0:
                self.proportions[c][root] = 1                

            self.proportions[c]["ratio"] = self.proportions[c][root] / self.proportions[c][contact]


        return self.proportions

    def compute_most_used_words(self, list_of_messages, top=10, threshold=3):
        words_counter = {}
        self.most_used_words = {}
        for msg in list_of_messages:
            words = msg.content.split(" ")
            for w in words:
                if len(w) > threshold:
                    w = w.decode("utf8")
                    w = w.replace("\r", "")
                    w = w.lower()
                    if w not in words_counter:
                        words_counter[w] = 1
                    else:
                        words_counter[w] += 1
        sorted_words = sorted(words_counter.iteritems(), key=operator.itemgetter(1), reverse=True)
        self.most_used_words = sorted_words[:top]
        return self.most_used_words

    def compute_avg_root_response_time(self):
        if (len(self.root_response_time) != 0):
            return sum(self.root_response_time)/len(self.root_response_time)
        return 0

    def compute_avg_contact_response_time(self):
        if (len(self.contact_response_time) != 0):
            return sum(self.contact_response_time)/len(self.contact_response_time)
        return 0

    def compute_response_time_ratio(self, root, contact):
        avg_root = self.compute_avg_root_response_time()
        avg_contact = self.compute_avg_contact_response_time()
        if (avg_contact != 0):
            return avg_root / avg_contact
        return 0

    def compute_bursts_ratio(self, root, contact):
        if (len(self.contact_burst)) == 0:
            return len(self.root_burst) / 1
        if (len(self.root_burst) == 0):
            return ( 1/len(self.contact_burst))
        return len(self.root_burst)/len(self.contact_burst)

    def compute_nbr_root_burst(self):
        return len(self.root_burst)
    
    def compute_nbr_contact_burst(self):
        return len(self.contact_burst)

    # def compute_avg_root_burst(self):
    #     if (len(self.root_burst) != 0):
    #         return sum(self.root_burst)/len(self.root_burst)
    #     return 0

    def compute_avg_contact_burst(self):
        if (len(self.contact_burst) != 0):
            return sum(self.contact_burst)/len(self.contact_burst)
        return 0

    def compute_root_initation_ratio(self, root, contact):
        if (self.initiations[contact] == 0):
            return self.initiations[root]/1
        if (self.initiations[root] == 0):
            return 1/self.initiations[contact] 
        return self.initiations[root] / self.initiations[contact]
        
    def generate_outcome(self, root, contact):
        outcome = 99;
        if (self.compute_root_initation_ratio(root, contact) > 0.867):
            outcome = 0 #"just not that into you"
            #print "DOESNT INITIATE"
        elif (self.proportions["qmarks"]["ratio"] < 0.87):
            outcome = 0 #"just not that into you"
            #print "QUESTIONS FAIL"
        else:
            outcome = 1 #"definitely into you"
            #print "ELSE"
        return outcome    
        
        
#        qMarksPerRoot = qmarksRoot/messagesRoot
 #       qMarksPerContact = qmarksContact/messagesContact
        
        
        
        