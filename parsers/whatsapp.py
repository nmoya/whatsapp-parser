from datetime import datetime
import message
import calendar

''' A line can be either: 
        09/12/2012 17:03:48: Sender Name: Message
        3/24/14, 1:59:59 PM: Sender Name: Message
        24/3/14, 13:59:59: Sender Name: Message
'''

class ParserWhatsapp():

    def __init__(self, raw_messages):
        self.raw_messages = raw_messages

    def parse(self):
        list_of_messages = []
        set_of_senders = set()
        for l in self.raw_messages:
            msg_date, sep, msg = l.partition(": ")
            raw_date, sep, time = msg_date.partition(" ")
            sender, sep, content = msg.partition(": ")
            # This ignores a minority of bad formatted lines.
            if len(raw_date) != 10 or len(time) != 8:
                continue
            raw_date = raw_date.replace(",", "")
            year = raw_date.split(" ")[0].split("/")[-1]
            # The following lines treats:
            # 3/24/14 1:59:59 PM
            # 24/3/14 13:59:59 PM
            # Couldn't we use msg_date instead of chatTimeString here?

            # colonIndex = [x.start() for x in re.finditer(':', l)]
            # print l, colonIndex
            # chatTimeString = l[0:colonIndex[2]]
            if "AM" in msg_date or "PM" in msg_date:
                datetime_obj = datetime.strptime(
                    msg_date, "%m/%d/%y, %I:%M:%S %p")
            else:
                if len(year) == 2:
                    datetime_obj = datetime.strptime(msg_date, "%d/%m/%y %H:%M:%S")
                else:
                    datetime_obj = datetime.strptime(msg_date, "%d/%m/%Y %H:%M:%S")

            set_of_senders.add(sender)
            list_of_messages.append(message.Message(sender, content, raw_date, time, datetime_obj))

        return list(set_of_senders), list_of_messages
