class Message():

    def __init__(self, from, to, content, date, time, datetime,
                 root_response_time, contact_response_time,
                 root_burst, contact_burst):
		self.from                  = from
		self.to                    = to
		self.content               = content
		self.date                  = date
		self.time                  = time
		self.datetime              = datetime
		self.root_response_time    = root_response_time
		self.contact_response_time = contact_response_time
		self.root_burst            = root_burst
		self.contact_burst         = contact_burst