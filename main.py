import datetime
import codecs


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
            try:
                columns = l.split(": ")
                date, time = columns[0].split(" ")
                sender = columns[1]
                self.datelist.append(date)
                self.timelist.append(time)
                self.senderlist.append(sender)
                self.messagelist.append(columns[2])
            except Exception:
                self.datelist.append(date)
                self.timelist.append(time)
                self.senderlist.append(sender)
                self.messagelist.append(l)

    def print_history(self):
        for i in range(len(c.messagelist)):
            print c.datelist[i], c.timelist[i],\
                c.senderlist[i], c.messagelist[i]


def main():
    c = Chat("Moyrilia.txt")
    c.open_file()
    c.feed_lists()


main()
