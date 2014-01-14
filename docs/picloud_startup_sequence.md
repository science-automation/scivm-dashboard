picloud warmup sequence
------------------------

On first call/map in the session the cloud cli try to get the api root endpoint and sync the local and remote packages.

First it reads the entry point from the config:
    
    ~/.picloud/cloudconfig.py
    server_list_url = 'http://api.picloud.com/servers/list/'

And executes the first query:

    POST http://api.picloud.com/servers/list/
    RESPONSE
    {"servers": ["https://api.picloud.com/"]}

Fetches the package list:

    POST https://api.picloud.com/package/list/?version=2.1 
    RESPONSE 
    {"packages": ["ArgImagePlugin", "BaseHTTPServer", "Bastion", ....]

Then it send some info (name, timestamp and ?is-archive flag) about all modules:

    POST https://api.picloud.com/module/check/?version=2.1
    DATA (gzipped json)
    [ [ u'IPython/core/error.py', 1385917079, False ], [ u'numpy/core/info.py', 1386462622, False ], [ u'IPython/external/ssh/forward.py', ... ] ]
    RESPONSE
    {"ap_version": "9ec1e9b6bd8346e586d5db417ba7dd5cc4f95a8a", "modules": [[ "asciitable/basic.py", 1386464225, false], ["asciitable/__init__.py", 1386464225, false],...]}

The response has an *ap_version* and the list of outdated/missing modules what need to be uploaded.

If there are missing/outdated modules, the cli try to upload them as a tar file:

    POST https://api.picloud.com/module/add/?version=2.1 
    DATA 
    [[u'asciitable/basic.py', 1386464223, False], ...]
    <tar file>
    RESPONSE
    {"ap_version": "3c1d1e25791799ef5bd486a5be29bde4f5e66959"}

And we got a new *ap_version* and the job gets submitted.

This *ap_version* seems to be a hash what gets calculated based on the package/module versions on the server. 
Probably there is a default environment for all user and all environment has an *ap_version*, maybe.

