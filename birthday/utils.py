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


"""Utility methods to be used throughout the app"""
import urllib

from google.appengine.api import users

def get_user_details(uri):
	"""Tool for get current user, login/out url, and relevant link text."""
	user = users.get_current_user()
	if user:
		url = users.create_logout_url(uri)
		url_linktext = 'Logout'
	else:
		url = users.create_login_url(uri)
		url_linktext = 'Login'
	return user, url, url_linktext

def isOwner(user, birthday):
	"""Checks ownership of a birthday object"""
	if user.user_id() == birthday.owner.identity:
		return True
	else:
		return False