# -*- coding: utf-8 -*-
from __future__ import division
from datetime import datetime
import codecs
import operator
import sys
import json
import csv
import argparse
from parsers import whatsapp
from parsers import facebook
from ChatFeatures import ChatFeatures


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

class Chat():

    def __init__(self, filename, platform="WhatsApp"):
        self.filename     = filename
        self.platform     = platform
        self.raw_messages = []
        self.messages     = []     # List of Messages objects
        self.features     = ChatFeatures() # Chat Features object
        self.senders      = []
        self.root         = ''

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
        dicts = json.loads(content)
        lines = dicts["data"]
        for l in lines:
            self.raw_messages.append(l)

    def parse_messages(self):
        if self.platform == "WhatsApp":
            p = whatsapp.ParserWhatsapp(self.raw_messages)
            self.senders, self.messages = p.parse()
        elif self.platform == "Facebook":
            p = facebook.ParserFacebook(self.raw_messages)
            self.senders, self.messages = p.parse()

    def set_root(self, root):
        self.root = root

    def get_contact(self):
        return list(set(self.senders).difference(set(self.root)))[0]

    def response_time_and_burst(self, root=None):
        if self.root is None:
            self.root = self.senders[0]
        return self.features.compute_response_time_and_burst(self.messages, self.root, self.senders)

    def messages_per_weekday(self):
        return self.features.compute_messages_per_weekday(self.messages)

    def messages_per_shift(self):
        return self.features.compute_messages_per_shift(self.messages)

    def messages_pattern(self):
        return self.features.compute_messages_pattern(self.messages, self.senders, self.patterns)

    def message_proportions(self):
        return self.features.compute_message_proportions(self.messages, self.senders, self.root, self.get_contact())

    def most_used_words(self):
        return self.features.compute_most_used_words(self.messages, 10, 3)
    
    def all_features(self, **kargs):
        burst_thrs = kargs.get("burst_thrs", 3)
        initiation_thrs = kargs.get("initiation_thrs", 60*60*8)
        response_thrs = kargs.get("response_thrs", 60*60*3)
        pattern_list = kargs.get("pattern_list", [])
        top = kargs.get("top", 10)
        word_length_threshold = kargs.get("word_length_threshold", 3)

        self.features.compute_response_time_and_burst(self.messages, self.root, self.senders, initiation_thrs, burst_thrs, response_thrs)
        self.features.compute_messages_per_weekday(self.messages)
        self.features.compute_messages_per_shift(self.messages)
        self.features.compute_messages_pattern(self.messages, self.senders, pattern_list)
        self.features.compute_message_proportions(self.messages, self.senders, self.root, self.get_contact())
        self.features.compute_most_used_words(self.messages, top, word_length_threshold)

    def print_features(self):
        print "Root: %s" % (self.senders[0])
        print ""

        print "Average root response time (s): %.2f" % (self.features.compute_avg_root_response_time())
        print "Average contact response time (s): %.2f" % (self.features.compute_avg_contact_response_time())
        print "Ratio: %.2f" % (self.features.compute_response_time_ratio(self.root, self.get_contact()))
        print ""

        # print "Number of root bursts: %d" % (self.features.compute_nbr_root_burst())
        # print "Average burst length: %.2ff" % (self.features.compute_avg_root_burst())
        # print ""

        print "Number of contact bursts: %d" % (self.features.compute_nbr_contact_burst())
        print "Average burst length: %.2ff" % (self.features.compute_avg_contact_burst())
        print "Ratio: %.2f" % (self.features.compute_bursts_ratio(self.root, self.get_contact()))
        print ""

        for s in self.senders:
            if s == self.root:
                print "Root initiations: %d" % (self.features.initiations[s])
            else:
                print "Contact initiations: %d" % (self.features.initiations[s])

        print "Root initiation ratio: %.2f" % (self.features.compute_root_initation_ratio(self.root, self.get_contact()))
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
            try: 
                print muw[0]
            except UnicodeEncodeError:
                self.features.most_used_words.remove(muw)

    def save_features(self, output_name):
        import pprint
        output = {}
        output["root"] = self.root
        output["avg_response_time"] = {}
        for s in self.senders:
            if s == self.root:
                output["avg_response_time"][s] = self.features.compute_avg_root_response_time()
            else:
                output["avg_response_time"][s] = self.features.compute_avg_contact_response_time()
        output["avg_response_time"]["ratio"] = self.features.compute_response_time_ratio(self.root, self.get_contact())

        output["nbr_bursts"] = {}
        for s in self.senders:
            if s == self.root:
                output["nbr_bursts"][s] = self.features.compute_nbr_root_burst()
            else:
                output["nbr_bursts"][s] = self.features.compute_nbr_contact_burst()
        output["nbr_bursts"]["ratio"] = self.features.compute_bursts_ratio(self.root, self.get_contact())

        # output["avg_bursts"] = {}
        # for s in self.senders:
        #     if s == self.root:
        #         output["avg_bursts"][s] = self.features.compute_avg_root_burst()
        #     else:
        #         output["avg_bursts"][s] = self.features.compute_avg_contact_burst()


        output["initiations"] = self.features.initiations
        output["initiations"]["root_initiation_ratio"] = self.features.compute_root_initation_ratio(self.root, self.get_contact())
        output["proportions"] = self.features.proportions
        output["weekdays"] = self.features.weekday
        output["shifts"] = self.features.shifts
        output["patterns"] = self.features.patterns
        output["senders"] = self.senders
        output["muw"] = self.features.most_used_words
        output["outcome"] = self.features.generate_outcome(self.root, self.get_contact(), 0) #TODO: make macros for outcome methodology 
        if output_name.endswith(".json"):
            arq = open(output_name, "w")
        else:
            arq = open(output_name+".json", "w")
        arq.write(json.dumps(output))
        pprint.pprint(output)
        arq.close()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chatlog Feature Extractor')
    parser.add_argument('-f', '--file', help='Chatlog file', required=True)
    parser.add_argument('-n', '--root', help='Root name', required=False)
    parser.add_argument('-p', '--platform', help='Platform', choices=["WhatsApp", "Facebook"], default="WhatsApp", required=False)
    parser.add_argument('-r', '--regexes', help='Regex patterns to compute frequency', nargs="+", required=False, default=[])
    parser.add_argument('-o', '--output', help='JSON output file name', required=False, default="./logs/basic_stats.json")

    args = vars(parser.parse_args())

    c = Chat(args["file"], args["platform"])
    c.open_file()
    c.parse_messages()
    if args.get("root") is None:
        for i, s in enumerate(c.senders):
            print str(i), s
        c.set_root(c.senders[int(raw_input("Please choose one person to be the root: "))])
    else:
        c.set_root(args["root"])
    c.all_features()
    c.print_features()
    c.save_features(args["output"])