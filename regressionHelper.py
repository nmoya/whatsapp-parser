import pickle

from HTMLParser import HTMLParser
import datetime,calendar
import csv
import math
import numpy as np

import Score_v2
import Peaps

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)
    def get_data(self):
        return ''.join(self.fed)

def html_to_text(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()




f = open("pl.dat","r")
pl = pickle.load(f)
f.close()


# Print names, emails, and context
#
# outputFile = open("peapListText.tsv", "w")
# outputFile.write("\t".join(["Primary name", "All names", "Emails", "ScopeScore","Last Contacted","NumberOfEmailsIncluded","ContextLocations","ContextOrganizations","ContextEducation"]) + "\n")
# for peap in pl.list:
# 	row = [peap.name, peap.names, peap.emails, peap.getScopeScore(), peap.getLastContacted(), len(peap.getMessageIDs()), peap.context["locations"], peap.context["organizations"], peap.context["education"]]

# 	outputFile.write("\t".join(map(str, row)) + "\n")

# 	print peap.name, "written"

# outputFile.close()

# Print score parameters
#
with open("contactsConsolidated.txt", "r") as csvfile:
    csvreader = csv.reader(csvfile, delimiter = ',')

    entries = [row for row in csvreader]

for row in entries:
    if len(row) != 13:
        print row
        raise Exception, "CSV format inconsistent"

for peap in pl.list:
    for row in entries:
        for email in peap.emails:
            for index in range(3, 13):
                if email == row[index]:
                    print "Match found between", peap.name, "(",peap.emails,") and ", row[index]

                    if row[1] == 'y':
                        peap.scopeInfo["scopeLabel"] = 1
                    else:
                        peap.scopeInfo["scopeLabel"] = 0

                    if row[2] == 'y':
                        peap.scopeInfo["priorityLabel"] = 1
                    else:
                        peap.scopeInfo["priorityLabel"] = 0
                        

d = datetime.datetime.utcnow()
now = 1.0*calendar.timegm(d.utctimetuple())/(24*60*60.0)


missingLabels = open("missingLabels.tsv", "w")
missingLabels.write("\t".join(["Primary name", "In scope", "Needs touch-up", "Emails"]) + "\n")

with open("addLabels.txt", "rU") as csvfile:
    csvreader = csv.reader(csvfile, delimiter = '\t')
    additionalLabels = [row for row in csvreader]

defaultOutOfScope = 0
numAdditionalLabels = 0
for peap in pl.list:
    if "scopeLabel" not in peap.scopeInfo.keys():
        for label in additionalLabels:
            if peap.name == label[0]:
                print "Additional match for", peap.name
                numAdditionalLabels += 1

                if label[1] == 'y':
                    peap.scopeInfo["scopeLabel"] = 1
                else:
                    peap.scopeInfo["scopeLabel"] = 0

                if label[2] == 'y':
                    peap.scopeInfo["priorityLabel"] = 1
                else:
                    peap.scopeInfo["priorityLabel"] = 0

    if ("scopeLabel" not in peap.scopeInfo.keys()) and peap.scopeInfo["scopeStatusAutomatic"] == -1:
        peap.scopeInfo["scopeLabel"] = 0
        peap.scopeInfo["priorityLabel"] = 0

        defaultOutOfScope += 1

    elif ("scopeLabel" not in peap.scopeInfo.keys()) and peap.scopeInfo["scopeStatusAutomatic"] == 1:
        # Include additional dataset
        print "No labeled data for", peap.name, "with emails", peap.emails
        missingLabels.write("\t".join([peap.name, "", "", str(peap.emails)]) + "\n")


outputFile = open("regressionData.tsv", "w")
outputFile.write("\t".join(["Primary name","scopeLabel","priorityLabel","normNumEmails","theta","normDuration","numSharedDomains","numAddresses","normEntropy","daysSinceLastContact","scopeStatusAutomatic","normInterTimeMean","normInterTimeMedian","normInterTimeSD"]) + "\n")


# Renormalize entropy - only for old datafiles
print "Renormalizing entropy - remove when using new datafiles"
# for peap in pl.list:
#     oldEntropy = peap.scopeInfo["normEntropy"]

#     if peap.scopeInfo["normDuration"] > 0:
#         peap.scopeInfo["normEntropy"] = (1.0 * oldEntropy * math.log(52)) / math.log(52 * peap.scopeInfo["normDuration"])
#     else:
#         peap.scopeInfo["normEntropy"] = 0
pl.calculateEntropies(365, 7)


# Analyze inter-message times
overallInterEmailTimes = []
for peap in pl.list:
    times,sender = Score_v2.get_time_sender(peap)

    for index in range(len(times) - 1):
        overallInterEmailTimes.append(times[index + 1] - times[index])

averageTime = np.mean(overallInterEmailTimes)
overallMedian = np.median(overallInterEmailTimes)
overallSD = np.std(overallInterEmailTimes)

print "Overall median", overallMedian
print "Average inter-email time:", averageTime
print "Total SD:", overallSD

for peap in pl.list:
    times, sender = Score_v2.get_time_sender(peap)

    peapInterEmailTimes = []
    for index in range(len(times) - 1):
        peapInterEmailTimes.append(times[index + 1] - times[index])

    if len(peapInterEmailTimes) > 0:
        peap.scopeInfo["normInterTimeMean"] = np.mean(peapInterEmailTimes) / averageTime
        peap.scopeInfo["normInterTimeMedian"] = np.median(peapInterEmailTimes) / overallMedian
        peap.scopeInfo["normInterTimeSD"] = np.std(peapInterEmailTimes) / overallSD
    else:
        peap.scopeInfo["normInterTimeMean"] = 999
        peap.scopeInfo["normInterTimeMedian"] = 999
        peap.scopeInfo["normInterTimeSD"] = 999





numWritten = 0
for peap in pl.list:
    if "scopeLabel" in peap.scopeInfo.keys():
        daysSinceLastContact = now - peap.getLastContacted()
        row = [peap.name, peap.scopeInfo["scopeLabel"], peap.scopeInfo["priorityLabel"], peap.scopeInfo["normNumEmails"],peap.scopeInfo["theta"],peap.scopeInfo["normDuration"],peap.scopeInfo["numSharedDomains"],peap.scopeInfo["numAddresses"],peap.scopeInfo["normEntropy"],daysSinceLastContact,peap.getScopeStatusAutomatic(),peap.scopeInfo["normInterTimeMean"],peap.scopeInfo["normInterTimeMedian"],peap.scopeInfo["normInterTimeSD"]]

        outputFile.write("\t".join(map(str, row)) + "\n")

        # print peap.name, "written"
        numWritten += 1
            


print "Written", numWritten, "out of", len(pl.list)
print "Defaulted to out of scope", defaultOutOfScope
print "Additional labels",  numAdditionalLabels

missingLabels.close()
outputFile.close()



# Print message bodies
#
# outputFile = open("messageBodies.txt", "w")
# for peap in pl.list:
# 	if "Armen Nalband" in peap.names:
# 		for messageID in peap.getMessageIDs():
# 			message = peap.getMessageByID(messageID)

# 			body = message["messageBody"]
# 			textBody = html_to_text(body)

# 			outputFile.write(textBody + "\n")
# outputFile.close()