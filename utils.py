from bson.codec_options import TypeCodec
from bson.codec_options import TypeRegistry
from bson.codec_options import CodecOptions


import os
import json

def clear_coll(collection):
	collection.delete_many({})


def special_check(ctx):
    return ctx.author.id == int(os.environ.get('MY_ID'))

def clear_dupes(file):
	with open(file, 'r') as f:
		data = json.load(f)
	cleaned = dict()
	for k in data:
		if data[k] not in cleaned.values():
			cleaned[len(cleaned) + 1] = data[k]
	with open(file, 'w') as f:
		json.dump(cleaned, f, indent=4)
class User():

	def __init__(self, name, id, mappings={}, words=[], occurrences=[], cipher={}):
		self.name = name
		self.id = id
		if mappings:
			self.mappings = mappings
		else:
			self.mappings = dict()
		if words:
			self.words = words
		else:
			self.words = list()
		if occurrences:
			self.occurrences = occurrences
		else:
			self.occurrences = list()
		# if cipher:
		# 	self._cipher = cipher
		# else:
		# 	self._cipher = dict()
		self._cipher = dict()
		self._start = 0
		self._dur = 0

	def getMax(self):
		return self.words[self.occurrences.index(self.getMaxOccur())]

	def newMax(self, n):
		if n > len(self.words):
			raise ValueError('Not enough messages.')
		def helper(n, words, occurrences):
			if n == 1:
				return words[occurrences.index(max(occurrences))], max(occurrences)
			else:
				words.pop(occurrences.index(max(occurrences)))
				occurrences.pop(occurrences.index(max(occurrences)))
				return helper(n - 1, words, occurrences)
		return helper(n, self.words[:], self.occurrences[:])

	def getMaxOccur(self):
		return max(self.occurrences)

	def __str__(self):
		return f'Name: {self.name}\nUID: {self.id}\nWords: {self.words}\nOccurrences: {self.occurrences}'

	def __repr__(self):
		return f'name={self.name} id={self.id} mappings={self.mappings} words={self.words} occurrences={self.occurrences}'

	@property
	def cipher(self):
		return self._cipher

	@cipher.setter
	def cipher(self, set):
		if len(set) != 26 and len(set) != 0:
			raise ValueError('Incorrect substitution cipher size.')
		self._cipher = set

	def scrambled(self):
		return bool(self._cipher)

	@property
	def start(self):
		return self._start
	
	@start.setter
	def start(self, set):
		if set < 0:
			raise ValueError('Negative time value.')
		self._start = set

	@property
	def dur(self):
		return self._dur

	@dur.setter
	def dur(self, set):
		if set < 0:
			raise ValueError('Negative duration.')
		self._dur = set


# https://api.mongodb.com/python/current/examples/custom_type.html 
class UserCodec(TypeCodec):
	python_type = User
	bson_type = list
	def transform_python(self, value):
		if isinstance(value, self.python_type):
			return ['User', value.name, value.id, value.mappings, value.words, value.occurrences]
		return value

	def transform_bson(self, value):
		if isinstance(value, self.bson_type) and value and value[0] == 'User':
			return User(value[1], value[2], value[3], value[4], value[5])
		else:
			return value

user_codec = UserCodec()
type_registry = TypeRegistry([user_codec])
codec_options = CodecOptions(type_registry=type_registry)


# from pymongo.son_manipulator import SONManipulator
# class Transform(SONManipulator):
# 	def transform_incoming(self, son, collection):
# 		for (key, value) in son.items():
# 			if isinstance(value, User):

# 				son[key] = encode_custom(value)
# 			elif isinstance(value, dict): # Make sure we recurse into sub-docs
# 				son[key] = self.transform_incoming(value, collection)
# 		return son

# 	def transform_outgoing(self, son, collection):
# 		for (key, value) in son.items():
# 			if isinstance(value, dict):
# 				if "_type" in value and value["_type"] == "custom":
# 					son[key] = decode_custom(value)
# 				else: # Again, make sure to recurse into sub-docs
# 					son[key] = self.transform_outgoing(value, collection)
# 		return son