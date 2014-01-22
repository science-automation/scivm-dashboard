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
