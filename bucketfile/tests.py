# Copyright 2014 Science Automation
#
# This file is part of Science VM.
#
# Science VM is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Science VM is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Science VM. If not, see <http://www.gnu.org/licenses/>.

from tastypie.test import ResourceTestCase
from django.contrib.auth.models import User
from bucketfiles.models import BucketFile

class BucketResourceTest(ResourceTestCase):
    #fixtures = ['test_applications.json']

    def setUp(self):
        super(BucketResourceTest, self).setUp()
        self.api_list_url = '/api/v1/bucketfile/'
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
            'testuser@example.com', self.password)
        self.api_key = self.user.get_default_apikey()

    def tearDown(self):
        super(BucketResourceTest, self).tearDown()

    def get_credentials(self):
        return self.create_apikey(self.username, self.api_key.key)

    def test_get_list_unauthorzied(self):
        """
        Test get without key returns unauthorized
        """
        self.assertHttpUnauthorized(self.api_client.get(self.api_list_url,
            format='json'))

    def test_get_list_json(self):
        """
        Test get application list
        """
        resp = self.api_client.get(self.api_list_url, format='json',
            authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
