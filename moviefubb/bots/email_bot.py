import smtplib, os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailBot():
	def __init__(self, email, psswd):		
		self.mime_msg = MIMEMultipart()
		self.family = []
		self.email = email
		self.psswd = psswd

	def appendRecipient(self, members):
		""" Append a Single Member or List of Members """
		if type(members) == list:
			for member in members:				
				if not member in self.family:
					self.family.append(member)
		if type(members) == str:
			if not member in self.family:
				self.family.append(member)

	def sendMessage(self, **kwargs):
		args = {
			'message': '',
			'sender': '',
			'subject': '',
		}
		COMMASPACE = ', '
		args_keys = args.keys()
		for key in kwargs.keys():
			if key in args_keys:
				args.update({key: kwargs[key]})

		self.mime_msg['Subject'] = args['subject']
		self.mime_msg['From'] = args['sender']
		self.mime_msg['To'] = COMMASPACE.join(self.family)
		self.mime_msg.attach(MIMEText(args['message'], 'html'))

		print 'Sending Message'
		s = smtplib.SMTP("smtp.gmail.com",587)
		s.ehlo()
		s.starttls()
		s.ehlo
		s.login(self.email, self.psswd)

		s.sendmail(args['sender'], self.family, self.mime_msg.as_string())
		s.quit()