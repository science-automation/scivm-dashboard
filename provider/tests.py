from tastypie.test import ResourceTestCase
from django.contrib.auth.models import User
from volume.models import Volume

class ProviderResourceTest(ResourceTestCase):
    #fixtures = ['test_applications.json']

    def setUp(self):
        super(ProviderResourceTest, self).setUp()
        self.api_list_url = '/api/v1/provider/'
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
            'testuser@example.com', self.password)
        self.api_key = self.user.get_default_apikey()

    def tearDown(self):
        super(ProviderResourceTest, self).tearDown()

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
