# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import datetime
from binascii import hexlify

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

import utils
from models import Owner, Birthday


JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader('templates'), #jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)
JINJA_ENVIRONMENT.globals = {
	'uri_for': webapp2.uri_for,
	'range':range
}
# [END imports]


class HomePage(webapp2.RequestHandler):
	def get(self):
		user, url, url_linktext = utils.get_user_details(self.request.uri)

		template_values = {
			'user': user,
			'url': url,
			'url_linktext': url_linktext,
		}

		template = JINJA_ENVIRONMENT.get_template('home.html')
		self.response.write(template.render(template_values))


class BdayListView(webapp2.RequestHandler):
	def get(self):

		user, url, url_linktext = utils.get_user_details(self.request.uri)
		user_id = user.user_id()

		now = datetime.date.today()
		currentMonthDay = "%02d" % (now.month) + "%02d" % (now.day)

		q1 = Birthday.query(
			user_id == Birthday.owner.identity
			).order(
			Birthday.monthday
			)
		q2 = q1.filter(
			Birthday.monthday >= currentMonthDay
			)
		q3 = q1.filter(
			Birthday.monthday < currentMonthDay
			)
		thisYearBDays = q2.fetch()
		nextYearBDays = q3.fetch() 

		birthdays = thisYearBDays + nextYearBDays
	
		template_values = {
			'user': user,
			'url': url,
			'url_linktext': url_linktext,
			'birthdays': birthdays,
		}

		template = JINJA_ENVIRONMENT.get_template('birthdaylist.html')
		self.response.write(template.render(template_values))

class BdayDetailView(webapp2.RequestHandler):
	def get(self, bday_id):

		user, url, url_linktext = utils.get_user_details(self.request.uri)

		bDay = Birthday.get_by_id(int(bday_id))

		if not utils.isOwner(user, bDay):
			self.response.set_status(403)
			return

		template_values = {
			'user': user,
			'url': url,
			'url_linktext': url_linktext,
			'birthday': bDay
		}

		template = JINJA_ENVIRONMENT.get_template('birthdaydetail.html')
		self.response.write(template.render(template_values))

class BdayCreateEditView(webapp2.RequestHandler):
	def get(self):

		user, url, url_linktext = utils.get_user_details(self.request.uri)

		now = datetime.datetime.now()
		currentYear = now.year

		template_values = {
			'user': user,
			'url': url,
			'url_linktext': url_linktext,
			'current_year': currentYear,
		}

		try:
			bday_id = self.request.get('edit')
			bDay = Birthday.get_by_id(int(bday_id)) 
			template_values['birthday'] = bDay
		except:
			pass

		template = JINJA_ENVIRONMENT.get_template('create_birthday.html')
		self.response.write(template.render(template_values))

	def post(self):
		
		user, url, url_linktext = utils.get_user_details(self.request.uri)

		# Get item if editing existing item, or creating new
		try:
			bday_id = self.request.get('edit')
			birthday = Birthday.get_by_id(int(bday_id))
		except:
			birthday = Birthday()

		birthdayDate = datetime.date(
			int(self.request.get('year')),
			int(self.request.get('month')),
			int(self.request.get('day')),
			)

		## Include 0's in month date
		formattedMonthDate = self.request.get('month') + self.request.get('day')

		birthday.firstName = self.request.get('first_name')
		birthday.lastName = self.request.get('last_name')
		birthday.date = birthdayDate
		birthday.owner = Owner(
                    identity=user.user_id(),
                    email=user.email())
        ## tags = self.request.get('tags') ## TODO
		## Additional values saved for sorting purposes
		birthday.monthday = formattedMonthDate

		birthday.put()
		self.redirect('/birthdays')

class BdayDeleteView(webapp2.RequestHandler):
	def get(self, bday_id):
		bDay = Birthday.get_by_id(int(bday_id)) 
		
		user, url, url_linktext = utils.get_user_details(self.request.uri)

		isOwner = True # TODO

		if (isOwner):
			# TODO
			isOwner = True

		bDay.delete_time_key  = datetime.datetime.now()

		bDay.delete_token = hexlify(os.urandom(16)).decode();

		bDay.put()

		template_values = {
			'user': user,
			'url': url,
			'url_linktext': url_linktext,
			'birthday': bDay
		}

		template = JINJA_ENVIRONMENT.get_template('birthdaydelete.html')
		self.response.write(template.render(template_values))
		


	def post(self, bday_id):
		try:
			bDay = Birthday.get_by_id(int(bday_id))
			token = self.request.get('token') 
		except:
			self.response.set_status(500)

		isOwner = True # TODO
		keyMatch = bDay.delete_token == token

		timeSinceDeleteRequest = datetime.datetime.now()-bDay.delete_time_key
		validTimeFrame = timeSinceDeleteRequest.seconds < (5*60)  

		if isOwner and keyMatch and validTimeFrame:
			bDay.key.delete()

		self.redirect('/birthdays')

def handle_404(request, response, exception):
    #logging.exception(exception)
    response.write('Oops! I could swear this page was here!')
    response.set_status(404)

def handle_500(request, response, exception):
    #logging.exception(exception)
    response.write('500. A server error occurred!')
    response.set_status(500)

app = webapp2.WSGIApplication([
	webapp2.Route(r'/', handler=HomePage, name='home'),
	webapp2.Route(r'/birthdays', handler=BdayListView, name='birthdayList'),
	webapp2.Route(r'/birthdays/create', handler=BdayCreateEditView, name='birthdayCreate'),
	webapp2.Route(r'/birthdays/delete/<bday_id>', handler=BdayDeleteView, name='birthdayDelete'),
	webapp2.Route(r'/birthdays/<bday_id>', handler=BdayDetailView, name='birthdayDetail'),
], debug=True) # TODO SET DEBUG TO FALSE

#app.error_handlers[404] = handle_404
#app.error_handlers[500] = handle_500