import os

"""
MODMAN_AS_SERVICE
    
    Use modman as a background service. If True the service must be started 
    or some api endpoints will not work properly.
"""
MODMAN_AS_SERVICE = os.environ.get("MODMAN_AS_SERVICE", False)


"""
MODMAN_SERVICE_ENDPOINT

    Zerorpc service endpoint to bind.
"""
MODMAN_SERVICE_ENDPOINT = os.environ.get("MODMAN_SERVICE_ENDPOINT", "tcp://127.0.0.1:10100")

"""
MODMAN_GIT_ROOT
    
    Root dir for user uploaded modules/repos.
"""
MODMAN_GIT_ROOT = os.path.realpath(os.environ.get("MODMAN_GIT_ROOT", os.path.join(os.path.expanduser("~"), ".modman/")))
