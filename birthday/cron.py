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
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

import webapp2

import utils
from settings import appSettings
from models import Owner, Birthday

class Summary(webapp2.RequestHandler):
	def get(self):

		now = datetime.date.today()
		currentMonthDay = "%02d" % (now.month) + "%02d" % (now.day)

		query = Birthday.query(projection=[Birthday.owner.identity], distinct=True)
		allUsers = query.fetch();
		birthdays = []

		for user in allUsers:

			q1 = Birthday.query(
				user.owner.identity == Birthday.owner.identity
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

			body = "Up coming birthdays:...."

			for birthday in birthdays:
				toEmail = birthday.owner.email
				body = body + birthday.firstName + birthday.lastName + "<br />"
				body = body + birthday.date.strftime("%B %d") + "<hr />"

			mail.send_mail(sender=appSettings["sender_address"],
                   to=toEmail,
                   subject="Your upcoming birthdays",
                   body=body)

		self.response.write("You have run birthdays cron job")

