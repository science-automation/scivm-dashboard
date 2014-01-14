from tastypie.api import Api

from .servers import CloudServerResource
from .modules import CloudPackageResource, CloudModuleResource
from .account import CloudAccountResource
from .job import CloudJobResource
from .bucket import CloudBucketResource
from .file_ import CloudFileResource
from .volume import CloudVolumeResource
from .cron import CloudCronResource
from .environment import CloudEnvironmentResource
from .queue import CloudQueueResource
from .realtime import CloudRealtimeResource
from .rest import CloudRestResource

cloud_api = Api(api_name='cloud')

cloud_api.register( CloudServerResource())
cloud_api.register( CloudPackageResource())
cloud_api.register( CloudModuleResource())
cloud_api.register( CloudAccountResource())
cloud_api.register( CloudJobResource())
cloud_api.register( CloudBucketResource())
cloud_api.register( CloudFileResource())
cloud_api.register( CloudVolumeResource())
cloud_api.register( CloudCronResource())
cloud_api.register( CloudEnvironmentResource())
cloud_api.register( CloudQueueResource())
cloud_api.register( CloudRestResource())
cloud_api.register( CloudRealtimeResource())

