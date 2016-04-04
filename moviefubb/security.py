import os, datetime
from hashlib import sha1
from .models import (DBSession, User)

super_secret_key = """\x81JZ\xbey\x998Io\xcaT\x16\xaa5\xe6\x88v\x966\x0e\x8d9N\xf3\x8e,\xa7d\x15n\xa4i\xcfJ\x9cQ\xc4\xda\xa01\x9e\x05/y\x9d:(\xfe-\xcc\x01\xf69\x8b\xa5V\xea\xe7xR"""

def groupfinder(userid, request):
	user = DBSession.query(User).filter_by(email=userid).first()
	if user is None:
		return []
	else:
		return [g.groupname for g in user.mygroups]

def hashpassword(password):
	if isinstance(password, unicode):
		password_8bit = password.encode('UTF-8')
	else:
		password_8bit = password

	salt = sha1()
	salt.update(super_secret_key)

	hash = sha1()
	hash.update(password_8bit + salt.hexdigest())
	digest = hash.hexdigest()

	if not isinstance(digest, unicode):
		digest = digest.decode('UTF-8')

	return (digest)

def generateConfirmationCode(user_id):
	""" The Confirmation ID is the UNIX time stamp and the User ID"""
	confirmation_string = str(datetime.datetime.now())
	for charx in ['-', ':', '_', ' ', '.']:
		confirmation_string = confirmation_string.replace(charx, "")
	confirmation_string += str(user_id)
	return (confirmation_string)