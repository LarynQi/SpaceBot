from bson.codec_options import TypeCodec
from bson.codec_options import TypeRegistry
from bson.codec_options import CodecOptions

def clear_coll(collection):
	collection.delete_many({})


def special_check(ctx):
    return ctx.author.id == int(os.environ.get('MY_ID'))

class User():

	def __init__(self, name, id, mappings={}, words=[], occurrences=[]):
		self.name = name
		self.id = id
		self.mappings = mappings
		self.words = words
		self.occurrences = occurrences

	def getMax(self):
		return self.words[self.occurrences.index(self.getMaxOccur())]

	def getMaxOccur(self):
		return max(self.occurrences)

	def __str__(self):
		return f'Name: {self.name}\nUID: {self.id}\nWords: {self.words}\nOccurrences: {self.occurrences}'

	def __repr__(self):
		return f'name={self.name} id={self.id} mappings={self.mappings} words={self.words} occurrences={self.occurrences}'

# https://api.mongodb.com/python/current/examples/custom_type.html 
class UserCodec(TypeCodec):
	python_type = User
	bson_type = list
	def transform_python(self, value):
		if isinstance(value, User):
			return ['User', value.name, value.id, value.mappings, value.words, value.occurrences]
		return value

	def transform_bson(self, value):
		if isinstance(value, list) and value[0] == 'User':
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