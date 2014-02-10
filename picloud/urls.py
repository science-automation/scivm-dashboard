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

from tastypie.api import Api

from .servers import CloudServerResource
from .modules import CloudPackageResource, CloudModuleResource
from .key import CloudKeyResource
from .job import CloudJobResource
from .bucket import CloudBucketResource
from .file_ import CloudFileResource
from .volume import CloudVolumeResource
from .cron import CloudCronResource
from .env import CloudEnvironmentResource
from .queue import CloudQueueResource
from .realtime import CloudRealtimeResource
from .rest import CloudRestResource
from .report import CloudReportResource

cloud_api = Api(api_name='cloud')

cloud_api.register( CloudServerResource())
cloud_api.register( CloudPackageResource())
cloud_api.register( CloudModuleResource())
cloud_api.register( CloudKeyResource())
cloud_api.register( CloudJobResource())
cloud_api.register( CloudBucketResource())
cloud_api.register( CloudFileResource())
cloud_api.register( CloudVolumeResource())
cloud_api.register( CloudCronResource())
cloud_api.register( CloudEnvironmentResource())
cloud_api.register( CloudQueueResource())
cloud_api.register( CloudRestResource())
cloud_api.register( CloudRealtimeResource())
cloud_api.register( CloudReportResource())

