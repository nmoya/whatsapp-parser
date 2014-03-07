import codecs
import date
import re

class Chat():
    def __init__(self, filename):
        self.filename = filename
        self.raw_messages = []

        self.datelist = []
        self.timelist = []
        self.senderlist = []
        self.messagelist = []

    def open_file(self):
        arq = open(self.filename)
        content = arq.read()
        arq.close()
        lines = content.split("\n")
        lines = [l for l in lines if len(l) != 1]
        for l in lines:
            a = l.decode("utf8", "ignore")
            self.raw_messages.append(a.encode("utf8"))

    def feed_lists(self):
        for l in self.raw_messages:
            search_obj = re.search(r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}', l)
            if search_obj:
                columns = l.split(": ")
                date, time = columns[0].split(" ")
                sender = columns[1]
                message = columns[2]
            else:
                message = l
            self.datelist.append(date)
            self.timelist.append(time)
            self.senderlist.append(sender)
            self.messagelist.append(message)

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
        for i in range(len(self.datelist[:10])):
            day, month, year = self.datelist[i].split("/")
            parsed_date = "%s-%s-%s" % (year, month, day)
            print parsed_date, date.date_to_weekday(parsed_date)

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
                shifts["latenight"]+=1

            elif hour > 6 and hour <= 11:
                shifts["morning"] +=1

            elif hour > 11 and hour <= 17:
                shifts["afternoon"] +=1

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
            pattern_dict[pattern] = re.compile(pattern, re.I)
        for i in range(len(self.messagelist)):
            for pattern in patternlist:
                search_result = pattern_dict[pattern].findall(self.messagelist[i])
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
        for s in senders:
            counter[s] = 0
        for i in range(len(self.senderlist)):
            counter[self.senderlist[i]] += 1
        total = 0
        for s in senders:
            total += counter[s]
        counter["total"] = total
        return counter

def main():
    c = Chat("Moyrilia.txt")
    c.open_file()
    c.feed_lists()
    c.print_patterns_dict(c.count_messages_pattern(['te amo', 'beijos', 'feliz', ':\)']))
    print c.message_proportions()

main()
