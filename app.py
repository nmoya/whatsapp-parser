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


class Chat():

    def __init__(self, filename, platform="Facebook"):
        self.filename = filename
        self.platform = platform
        self.raw_messages = []
        self.messages = []     # List of Messages objects
        self.senders = []
        self.root_initiations = 0
        self.contact_initiations = 0
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
            self.messages = p.parse()
        elif self.platform == "Facebook":
            p = facebook.ParserFacebook(self.raw_messages)
            self.messages = p.parse()


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
