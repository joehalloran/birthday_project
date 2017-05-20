from google.appengine.ext import ndb

# [START models]

class Owner(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=False)

class Birthday(ndb.Model):
	"""A main model for representing an individual birthday entry."""
	owner = ndb.StructuredProperty(Owner) 
	firstName = ndb.StringProperty('fn') # indexed=True by default
	lastName = ndb.StringProperty('ln') # indexed=True by default
	date = ndb.DateProperty(auto_now_add=True)
	## Additional values saved for sorting purposes
	monthday = ndb.StringProperty() # indexed=True by default
	## End additional date values
	tags = ndb.StringProperty(repeated=True) # indexed=True by default
	creation_date = ndb.DateTimeProperty('cd',auto_now_add=True)
	modified_date = ndb.DateTimeProperty('md',auto_now=True)
	delete_token = ndb.TextProperty() # indexed=False by default
	delete_time_key = ndb.DateTimeProperty()

	

# [END models]