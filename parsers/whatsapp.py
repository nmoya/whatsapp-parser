import message

class ParserWhatsapp():

    def __init__(self, raw_messages):
        self.raw_messages = raw_messages

    def parse(self):
        list_of_messages = []
        list_of_senders  = []
        for l in self.raw_messages:
            m = dict()
            msg_date, sep, msg = l.partition(": ")
            raw_date, sep, time = msg_date.partition(" ")
            sender, sep, message = msg.partition(": ")
            if len(raw_date) != 10: # This ignores a minority of bad formatted lines.
                continue
            print raw_date, "*", time, "*", sender, "*", message
            continue
            #print ("\n\n\nRAW: ")
            #print (raw_date)
            raw_date = raw_date.replace(",", "")
            #print (raw_date)
            #print ("\n\n\n")
            if message:
                self.datelist.append(raw_date)
                self.timelist.append(time)  # here is the time object; save it
                colonIndex = [x.start() for x in re.finditer(':', l)]
                # print ind
                # grab the characters that make up the date and time (Everthing
                # until the third colon
                chatTimeString = l[0:colonIndex[2]]

                if "AM" in chatTimeString or "PM" in chatTimeString:
                    # convert to a data object, format of the whatsapp data
                    # 8/2/14, 12:59:24 PM
                    chatTime = datetime.strptime(
                        chatTimeString, "%m/%d/%y, %I:%M:%S %p")
                else:
                    # convert to a data object, format of the whatsapp data
                    # 8/2/14, 12:59:24 PM
                    chatTime = datetime.strptime(
                        chatTimeString, "%d/%m/%y %H:%M:%S")


# chatTime = datetime.strptime(chatTimeString, "%m/%d/%y, %I:%M:%S %p")
# convert to a data object, format of the whatsapp data 8/2/14, 12:59:24
# PM
                self.chatTimeList.append(chatTime)
                self.senderlist.append(sender)
                self.messagelist.append(message)
            else:
                self.messagelist.append(l)
        t0 = self.chatTimeList[0]
        senderIndex = 0
        # variable to count the number of messages in a row sent by sender
        burstCount = 1

        rootName = "ROOT"
        contactName = "CONTACT"
        INITIATION_THRESHOLD = (8 * 60 * 60)

        # perform the operations that are dependant on multiple messages
        # (response time, bursts)
        for t1 in self.chatTimeList[1:]:
            dt = t1 - t0
            # is sender the same as the last message?
            if self.senderlist[senderIndex] != self.senderlist[senderIndex - 1]:
                # sender changed, store the burst count and reset
                #                print("sender changed: %s") %(self.senderlist[senderIndex])
                if (dt.seconds > INITIATION_THRESHOLD):
                    if self.senderlist[senderIndex] == rootName:
                        self.rootInitiations += 1
                    elif self.senderlist[senderIndex] == contactName:
                        self.contactInitiations += 1
                    else:
                        sys.exit(
                            "ERROR CHANGE NAMES IN CHAT TO ROOT AND CONTACT1\n")
                #print("response time: %d\n" %(dt.seconds) )
                # is sender the root?
                if self.senderlist[senderIndex] == rootName:
                    # store the burst count for the last sender, which is the
                    # opposite of current
                    self.contactBurstList.append(burstCount)
                    self.rootResponseTimeList.append(dt.seconds)
                # is sender the contact?
                elif self.senderlist[senderIndex] == contactName:
                    # store the burst count for the last sender, which is the
                    # opposite of current
                    self.rootBurstList.append(burstCount)
                    self.contactResponseTimeList.append(dt.seconds)
                else:
                    errorName = self.senderlist[senderIndex]
                    sys.exit(
                        "ERROR CHANGE NAMES IN CHAT TO ROOT AND CONTACT2\n")
                burstCount = 1

                # save

            else:
                # accumulate the number of messages sent in a row
                burstCount += 1
                if burstCount >= 3:
                    print"bursting: %d %s\n" % (burstCount, self.senderlist[senderIndex])
                # print"repeat sender: %d %s\n" %(burstCount,
                # self.senderlist[senderIndex])

            # self.responseTimeList.append(dt.seconds)
            t0 = t1
            senderIndex += 1
