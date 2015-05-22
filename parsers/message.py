class Message():

    def __init__(self, sender, content, date, time, datetime_obj):
		self.sender                = sender
		self.content               = content
		self.date                  = date
		self.time                  = time
		self.datetime_obj          = datetime_obj

	def __repr__(self):
		return " ".join([self.datetime_obj, self.sender, self.content])