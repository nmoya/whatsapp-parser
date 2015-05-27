# -*- coding: utf-8 -*-
from __future__ import division
from datetime import datetime
import codecs
import datelib
import re
import operator
import sys
import json
import csv
import argparse
from parsers import whatsapp
from parsers import facebook


def pretty_print(dic, parent, depth):
    tup = sorted(dic.iteritems(), key=operator.itemgetter(1))
    isLeaf = True
    for key in tup:
        if isinstance(dic[key[0]], dict):
            isLeaf = False
    if isLeaf and depth != 0:
        print " " * (depth - 1) * 2, parent
    for key in tup:
        if isinstance(dic[key[0]], dict):
            pretty_print(dic[key[0]], key[0], depth + 1)
        else:
            print " " * depth * 2, str(key[0]), "->", dic[key[0]]


class ChatFeatures():

    def __init__(self):
        self.root_response_time    = []
        self.contact_response_time = []
        self.root_burst            = []
        self.contact_burst         = []
        self.root_initiations      = 0
        self.contact_initiations   = 0
        self.weekday               = {}
        self.shifts                = {}
        self.patterns              = {}
        self.proportions           = {}
        self.most_used_words       = {}

    def compute_response_time_and_burst(self, list_of_messages, root_name, initiation_thrs=(60*60*8), burst_thrs=3):
        # perform the operations that are dependant on multiple messages
        # (response time, bursts)
        t0 = list_of_messages[0].datetime_obj
        burst_count = 1
        for index, message in enumerate(list_of_messages):
            if index == 0:
                continue
            t1 = message.datetime_obj
            dt = t1 - t0

            # is sender the same as the last message?
            if message.sender != list_of_messages[index-1].sender:
                # sender changed, store the burst count and reset
                # print "sender changed: %s" % ( message.sender )
                if (dt.seconds > initiation_thrs):
                    if message.sender == root_name:
                        self.root_initiations += 1
                    else:
                        self.contact_initiations += 1
                #print("response time: %d\n" %(dt.seconds) )
                # is sender the root?
                if message.sender == root_name:
                    # store the burst count for the last sender, which is the
                    # opposite of current
                    if burst_count > burst_thrs:
                        self.contact_burst.append(burst_count)
                    self.root_response_time.append(dt.seconds)
                # is sender the contact?
                else:
                    # store the burst count for the last sender, which is the
                    # opposite of current
                    if burst_count > burst_thrs:
                        self.root_burst.append(burst_count)
                    self.contact_response_time.append(dt.seconds)
                
                # End of the first burst, restart the counter
                burst_count = 1

            else:
                # accumulate the number of messages sent in a row
                burst_count += 1
                # if burst_count >= 3:
                #     print"bursting: %d %s\n" % (burst_count, message.sender)
            t0 = t1

    def compute_messages_per_weekday(self, list_of_messages):
        self.weekday = {}
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

    def compute_message_proportions(self, list_of_messages, senders):
        total = 0
        self.proportions = {}
        for i in ["messages", "words", "chars", "qmarks", "exclams", "media"]:
            self.proportions[i] = {}
            for s in senders:
                self.proportions[i][s] = 0
        for msg in list_of_messages:
            self.proportions["messages"][msg.sender] += 1
            self.proportions["words"][msg.sender]    += len(msg.content.split(" "))
            self.proportions["chars"][msg.sender]    += len(msg.content)
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
        self.proportions["total_messages"] = 0
        self.proportions["total_words"]    = 0
        self.proportions["total_chars"]    = 0
        self.proportions["total_qmarks"]   = 0
        self.proportions["total_exclams"]  = 0
        self.proportions["total_media"]    = 0

        self.proportions["avg_words"] = {}

        for s in senders:
            self.proportions["total_messages"] += self.proportions["messages"][s]
            self.proportions["total_words"] += self.proportions["words"][s]
            self.proportions["total_chars"] += self.proportions["chars"][s]
            self.proportions["total_qmarks"] += self.proportions["qmarks"][s]
            self.proportions["total_exclams"] += self.proportions["exclams"][s]
            self.proportions["total_media"] += self.proportions["media"][s]
            self.proportions["avg_words"][s] = self.proportions["words"][s] / self.proportions["messages"][s]

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
        return sum(self.root_response_time)/len(self.root_response_time)

    def compute_avg_contact_response_time(self):
        return sum(self.contact_response_time)/len(self.contact_response_time)

    def compute_nbr_root_burst(self):
        return len(self.root_burst)
    
    def compute_nbr_contact_burst(self):
        return len(self.contact_burst)

    def compute_avg_root_burst(self):
        return sum(self.root_burst)/len(self.root_burst)

    def compute_avg_contact_burst(self):
        return sum(self.contact_burst)/len(self.contact_burst)

    def compute_root_initation_ratio(self):
        return self.root_initiations / self.contact_initiations


class Chat():

    def __init__(self, filename, platform="Facebook", _string=False):
        self.filename            = filename
        self.platform            = platform
        self.raw_messages        = []
        self.messages            = []     # List of Messages objects
        self.features            = ChatFeatures() # Chat Features object
        self.senders             = []
        if _string:
            if platform == "Facebook":
                self.open_file = self.open_file_string_facebook
        else:
            if platform == "WhatsApp":
                self.open_file = self.open_file_whatsapp
            elif platform == "Facebook":
                self.open_file = self.open_file_facebook_json

    def open_file_whatsapp(self):
        arq = codecs.open(self.filename, "r", "utf-8-sig")
        content = arq.read()
        arq.close()
        lines = content.split("\n")
        lines = [l for l in lines if len(l) != 1]
        for l in lines:
            self.raw_messages.append(l.encode("utf-8"))

    def open_file_facebook_json(self):
        arq = codecs.open(self.filename, "r", "utf-8-sig")
        content = arq.read()
        arq.close()
        lines = content.split("\n")
        lines = [l for l in lines if len(l) != 1]
        for l in lines:
            self.raw_messages.append(l.encode("utf-8"))

    def open_file_string_facebook(self):
        dicts = json.loads(self.filename)
        print dicts

    def parse_messages(self):
        if self.platform == "WhatsApp":
            p = whatsapp.ParserWhatsapp(self.raw_messages)
            self.senders, self.messages = p.parse()
        elif self.platform == "Facebook":
            p = facebook.ParserFacebook(self.raw_messages)
            self.senders, self.messages = p.parse()

    def response_time_and_burst(self, root=None):
        if root is None:
            print "Root is ", self.senders[0]
            return self.features.compute_response_time_and_burst(self.messages, self.senders[0])
        else:
            return self.features.compute_response_time_and_burst(self.messages, root)

    def messages_per_weekday(self):
        return self.features.compute_messages_per_weekday(self.messages)

    def messages_per_shift(self):
        return self.features.compute_messages_per_shift(self.messages)

    def messages_pattern(self):
        return self.features.compute_messages_pattern(self.messages, self.senders, self.patterns)

    def message_proportions(self):
        return self.features.compute_message_proportions(self.messages, self.senders)

    def most_used_words(self):
        return self.features.compute_most_used_words(self.messages, 10, 3)
    
    def all_features(self, **kargs):
        root_name = kargs.get("root_name", self.senders[0])
        burst_thrs = kargs.get("burst_thrs", 3)
        initiation_thrs = kargs.get("initiation_thrs", 60*60*8)
        pattern_list = kargs.get("pattern_list", ["amor"])
        top = kargs.get("top", 10)
        word_length_threshold = kargs.get("word_length_threshold", 3)

        self.features.compute_response_time_and_burst(self.messages, root_name, initiation_thrs, burst_thrs)
        self.features.compute_messages_per_weekday(self.messages)
        self.features.compute_messages_per_shift(self.messages)
        self.features.compute_messages_pattern(self.messages, self.senders, pattern_list)
        self.features.compute_message_proportions(self.messages, self.senders)
        self.features.compute_most_used_words(self.messages, top, word_length_threshold)

    def print_features(self):
        print "Root: %s" % (self.senders[0])
        print ""

        print "Average root response time (s): %.2f" % (self.features.compute_avg_root_response_time())
        print "Average contact response time (s): %.2f" % (self.features.compute_avg_contact_response_time())
        print ""

        print "Number of root bursts: %d" % (self.features.compute_nbr_root_burst())
        print "Average burst length: %.2ff" % (self.features.compute_avg_root_burst())
        print ""

        print "Number of contact bursts: %d" % (self.features.compute_nbr_contact_burst())
        print "Average burst length: %.2ff" % (self.features.compute_avg_contact_burst())
        print ""

        print "Root initiations: %d" % (self.features.root_initiations)
        print "Contact initiations: %d" % (self.features.contact_initiations)
        print "Root initiation ratio: %.2f" % (self.features.compute_root_initation_ratio())
        print ""

        print "Proportions:"
        pretty_print(self.features.proportions, self.features.proportions.keys()[0], 1)
        print ""
        print "Weekdays:"
        pretty_print(self.features.weekday, "Weekday", 0)
        print ""
        print "Shifts:"
        pretty_print(self.features.shifts, "Shifts", 0)
        print ""
        print "Patterns:"
        pretty_print(self.features.patterns, "Patterns", 0)
        print ""
        print "Most used words:"
        for muw in self.features.most_used_words:
            print muw[0]

    def save_features(self, output_name):
        import pprint
        output = {}
        output["root"] = self.senders[0]
        output["avg_root_response_time"] = self.features.compute_avg_root_response_time()
        output["avg_contact_response_time"] = self.features.compute_avg_contact_response_time()
        output["nbr_root_burst"] = self.features.compute_nbr_root_burst()
        output["nbr_contact_burst"] = self.features.compute_nbr_contact_burst()
        output["avg_root_burst"] = self.features.compute_avg_root_burst()
        output["avg_contact_burst"] = self.features.compute_avg_contact_burst()
        output["root_initiations"] = self.features.root_initiations
        output["contact_initiations"] = self.features.contact_initiations
        output["root_iniation_ratio"] = self.features.compute_root_initation_ratio()
        output["proportions"] = self.features.proportions
        output["weekdays"] = self.features.weekday
        output["shifts"] = self.features.shifts
        output["patterns"] = self.features.patterns
        output["muw"] = self.features.most_used_words
        if output_name.endswith(".json"):
            arq = open(output_name, "w")
        else:
            arq = open(output_name+".json", "w")
        arq.write(json.dumps(output))
        pprint.pprint(output)
        arq.close()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chatlog Feature Extractor')
    parser.add_argument('-p', '--platform', help='Platform', choices=["WhatsApp", "Facebook"], required=True)
    parser.add_argument('-f', '--file', help='Chatlog file', required=False)
    parser.add_argument('-r', '--regexes', help='Regex patterns to compute frequency', nargs="+", required=False, default=[])
    parser.add_argument('-o', '--output', help='JSON output file name', required=False, default="./logs/basic_stats.json")
    parser.add_argument('-s', '--string', help='Receive the chat as string', required=False, default=False)

    args = vars(parser.parse_args())

    if args["string"] is not False:
        c = Chat(args["string"], args["platform"], _string=True)
    else:
        c = Chat(args["file"], args["platform"])
    c.open_file()
    c.parse_messages()
    c.all_features()
    c.print_features()
    c.save_features(args["output"])