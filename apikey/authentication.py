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

import base64

from django.conf import settings
from tastypie.http import HttpUnauthorized
from tastypie.authentication import (
    Authentication, ApiKeyAuthentication, SessionAuthentication,
    MultiAuthentication
)
from django.contrib.auth.models import User

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

try:
    import python_digest
except ImportError:
    python_digest = None

try:
    import oauth2
except ImportError:
    oauth2 = None

try:
    import oauth_provider
except ImportError:
    oauth_provider = None


class MultiApiKeyAuthentication(ApiKeyAuthentication):

    def is_authenticated(self, request, **kwargs):
        """
        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """

        username, api_secretkey = self.extract_credentials(request)
        if not username or not api_secretkey:
            return self._unauthorized()

        apikey = self.get_key(username, api_secretkey)
        if apikey is None:
            return self._unauthorized()

        user = apikey.user

        if not self.check_active(user):
            return False

        request.user = user
        request.apikey = apikey

        return True

    def get_key(self, username, api_secretkey):
        from .models import ApiKey

        try:
            return ApiKey.objects.select_related("user",).get(
                user__username=username, key=api_secretkey, enabled=True
            )
        except ApiKey.DoesNotExist:
            return None

    def get_identifier(self, request):
        if hasattr(request, "user") and hasattr(request.user, "username"):
            return request.user.username
        return 'nouser'


class SciCloudApiKeyAuthentication(Authentication):
    """ a remix of ApiKeyAuthentication and BasicAuthentication """

    def _unauthorized(self):
        return HttpUnauthorized()

    def extract_credentials(self, request):
        if settings.DEBUG and settings.API_DEBUG_AUTH_USERNAME:
            # FIXME remove this code
            try:
                user = User.objects.get(
                    username=settings.API_DEBUG_AUTH_USERNAME
                )
                apikey = user.get_default_apikey()
                if apikey is None:
                    return None, None
                return apikey.pk, apikey.key
            except (User.DoesNotExist, IndexError):
                pass

        if request.META.get('HTTP_AUTHORIZATION'):

            parts = request.META['HTTP_AUTHORIZATION'].split()
            if len(parts) != 2 and parts[0].lower() != 'basic':
                return None, None

            creds = base64.b64decode(parts[1]).split(':', 1)
            if len(creds) == 2:
                return creds

            return None, None

    def is_authenticated(self, request, **kwargs):
        """
            Should return either ``True`` if allowed, ``False`` if not or an
            ``HttpResponse`` if you need something custom.
            """

        api_key, api_secretkey = self.extract_credentials(request)
        if not api_key or not api_secretkey:
            return self._unauthorized()

        apikey = self.get_key(api_key, api_secretkey)
        if apikey is None:
            return self._unauthorized()

        user = apikey.user

        if not self.check_active(user):
            return False

        request.user = user
        request.apikey = apikey if apikey.pk is not None else None

        return True

    def get_key(self, api_key, api_secretkey):
        from .models import ApiKey

        try:
            return ApiKey.objects.select_related("user",).get(
                pk=api_key, key=api_secretkey, enabled=True
            )
        except ApiKey.DoesNotExist:
            return None
        except ValueError:
            pass

        # try to authenticate by email/password
        try:
            user = User.objects.get(email=api_key)
            if not user.check_password(api_secretkey):
                return None
        except User.DoesNotExist:
            return None

        apikey = ApiKey(user=user)
        return apikey

    def get_identifier(self, request):
        if hasattr(request, "user") and hasattr(request.user, "username"):
            return request.user.username
        return 'nouser'
