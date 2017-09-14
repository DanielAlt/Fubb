import datetime, re

_number = 0
_select = 1
_text = 2
_bool = 3

class InvalidDataType(Exception):
    def __init___(self, dataType):
        Exception.__init__(self, ("Invalid Data Type: %s" % dataType))
        self.dataType = dataType

class Field():

	def __init__(self, f_name, f_type, **kwargs):
		self.f_name = f_name
		self.f_type = f_type
		self.args = dict(
			int_min = None,
			int_max = None,
			int_len = None,
			text_min = None,
			text_max = None,
			text_reg = None,
			select_opts = None,
			bool_force = None,
		)
		for key in kwargs.keys():
			if key in self.args.keys():
				self.args.update({key: kwargs[key]})

	def isValid(self, value):
		""" 
			Determine if input is Valid Based on the Type of Input Specified
			And the Initial Class Arguments provided in KWARGS.
		"""
		if (self.f_type == _number):
			try:
				valid = True
				int(value)
				if (self.args['int_max'] is not None):
					if not (int(value) <= self.args['int_max']):
						valid = False
				if (self.args['int_min'] is not None):
					if not (int(value) >= self.args['int_min']):
						valid = False
				if (self.args['int_len'] is not None):
					if not (len(value) == self.args['int_len']):
						valid = False
				return (valid)

			except ValueError:
				return False

		elif (self.f_type == _select):
			valid = True
			
			if (self.args['select_opts'] is not None):
				if not (value in self.args['select_opts']):
					valid = False

			return (valid)

		elif (self.f_type == _text):
			valid = True
			
			if self.args['text_max'] is not None:
				if not (len(value) <= self.args['text_max']):
					valid = False
			if self.args['text_min'] is not None:
				if not (len(value) >= self.args['text_min']):
					valid = False
			if self.args['text_reg'] is not None:
				if (self.args['text_reg'].match(value) is None):
					valid = False

			return (valid)

		elif (self.f_type == _bool):
			valid = True

			if self.args['bool_force'] is not None:
				
				if self.args['bool_force']:
					if ((not value) or not (value.lower() == 'true')):
						valid = False

				if self.args['bool_force'] == False:
					if (value) or not (value.lower() == 'false'):
						valid = False

			return (valid)

		else:
			raise InvalidDataType(self.f_type)

class Form():
	def isValid(self, form_data):
		validity_legend = {}
		for field in self.fields:
			if (field.isValid(form_data[field.f_name])):
				validity_legend.update({field.f_name: True})
			else:
				validity_legend.update({field.f_name: False})

		valid = True
		for key in validity_legend.keys():
			if not validity_legend[key]:
				valid = False

		# if not (len(form_data.keys()) == len(self.fields)):
		# 	valid = False

		if valid:
			return (True, form_data)

		else:
			return (False, validity_legend)

class AddUserForm(Form):
	def __init__(self):
		email_reg = re.compile('(\S)*@(\w)*\.\w{2,}')
		self.fields = [
			Field('email', _text, text_max=150, text_min=6, text_reg=email_reg),
			Field('username', _text, text_max=75, text_min =2),
			Field('password', _text, text_max=32, text_min=8),
			Field('terms_accepted', _bool, bool_force=True)
		]
		
class AddMovieForm(Form):
	def __init__(self):
		genre_reg = re.compile('#[a-zA-Z]* *')
		location_select = ["any", 'dvd', 'bluray', 'vhs', 'computer', 'hd']
		language_select = ['eng', 'fr', 'deu']
		status_w_select = ['watched', 'unwatched']
		status_dl_select = ['pending', 'downloading', 'downloaded', 'deleted']

		self.fields = [
			Field('title', _text, text_min=1, text_max=100),
			Field('year', _number, int_len=4),
			Field('genre_tags', _text, text_min=0, text_max=500, text_reg=genre_reg),
			Field('location', _select, select_opts=location_select),
			Field('language', _select, select_opts=language_select),
			Field('status_w', _select, select_opts=status_w_select),
			Field('status_dl', _select, select_opts=status_dl_select)
		]

class UpdateProfileForm(Form):
	def __init__(self):
		self.fields = [
			Field('fav_show', _text, text_min=0, text_max=100),
			Field('fav_film', _text, text_min=0, text_max=100),
			Field('fav_show', _text, text_min=0, text_max=100),
			Field('about_me', _text, text_min=0, text_max=1000),
		]

class UserPrivacyForm(Form):
	def __init__(self):
		privacy_opts = ['anyone', 'onlyme', 'fubbusers', 'friends']
		self.fields = [
			Field('show_profile', _select, select_opts=privacy_opts),
			Field('show_collection', _select, select_opts=privacy_opts),
			Field('show_stats', _select, select_opts=privacy_opts)
		]