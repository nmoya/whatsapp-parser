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
from parsers import whatsapp
from parsers import facebook


class ChatFeatures():

    def __init__(self):
        self.root_response_time    = []
        self.contact_response_time = []
        self.root_burst            = []
        self.contact_burst         = []
        self.root_initiations      = 0
        self.contact_initiations   = 0

    def compute_response_time_and_burst(self, list_of_messages, root_name, initiation_thrs=(60*60*8)):
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
                    self.contact_burst.append(burst_count)
                    self.root_response_time.append(dt.seconds)
                # is sender the contact?
                else:
                    # store the burst count for the last sender, which is the
                    # opposite of current
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


class Chat():

    def __init__(self, filename, platform="Facebook"):
        self.filename            = filename
        self.platform            = platform
        self.raw_messages        = []
        self.messages            = []     # List of Messages objects
        self.features            = ChatFeatures() # Chat Features object
        self.senders             = []
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

    def parse_messages(self):
        if self.platform == "WhatsApp":
            p = whatsapp.ParserWhatsapp(self.raw_messages)
            self.senders, self.messages = p.parse()
        elif self.platform == "Facebook":
            p = facebook.ParserFacebook(self.raw_messages)
            self.senders, self.messages = p.parse()

    def response_time_and_burst(self):
        print "Root is ", self.senders[0]
        self.features.compute_response_time_and_burst(self.messages, self.senders[0])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "ERROR: python app.py <chat_log> <WhatsApp|Facebook>"
        sys.exit(-1)

    options = ["WhatsApp", "Facebook"]
    if sys.argv[2] not in options:
        print "ERROR: Please choose one:"
        for o in options:
            print o
        sys.exit(-1)

    c = Chat(sys.argv[1], sys.argv[2])
    c.open_file()
    c.parse_messages()
    c.response_time_and_burst()
