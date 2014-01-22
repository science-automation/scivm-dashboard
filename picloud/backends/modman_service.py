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

import zerorpc

from conf import MODMAN_SERVICE_ENDPOINT, MODMAN_GIT_ROOT
from _dummy import PACKAGES_TO_IGNORE

import os
import sh
import tarfile
import StringIO
import logging
from sh import git

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Service(object):

    def packages_to_ignore(self, **kwargs):
        logger.info("packages_to_ignore call")
        # FIXME 
        # -- this is the original response of picloud; 
        # -- we need to implement our solution
        return PACKAGES_TO_IGNORE

    def check_modules(self, user_id, module_descs_in, **kwargs):
        logger.info("check_modules call")
        # TODO no check yet; compare to what?
        # FIXME asking for all modules
        response = {}
        response["modules_to_upload"] = module_descs_in
        return response
    
    def add_modules(self, user_id, module_descs_in, tarfile_raw, **kwargs):
        # FIXME this version is dummy, creates only a new branch based on existing+incoming files
        logger.info("add_modules call")
        ap_version = ""
        
        self.create_repo_for_user_id(user_id)

        # open tarfile
        stream = StringIO.StringIO(tarfile_raw)
        with tarfile.open(fileobj=stream, mode="r") as f:
            members = f.getmembers()
            if members:
                logger.info("tarfile has some files: {0}".format(members,))
                
                main_dir = self.main_dir_for_user_id(user_id)
                logger.info("using main dir {0}".format(main_dir,))
                
                #TODO some kind of locking would be good here
                # don't let it go concurrently for the same user_id
                    
                # extracting files from tarfile
                f.extractall(main_dir)
                
                # adding changes to the repository
                git.add("-A",  _cwd=main_dir)

                # check if there any changes
                if git.status("-s", _cwd=main_dir):
                    logger.info("need to commit in {0}".format(main_dir,))

                    # commit
                    git.commit("-m", "modules added/updated", _cwd=main_dir)
                    
                    # get last commit id
                    last_id = git.log('-1', "--format=%H", '--no-color', _cwd=main_dir, _tty_out=False).stdout.strip()

                    # create and checkout branch in a subdir of user base dir
                    git.branch(last_id, _cwd=main_dir)
                    git("checkout-index", "-a", "--prefix=../{0}/".format(last_id,), _cwd=main_dir)

                    # back to master
                    git.checkout("master", _cwd=main_dir)

                    ap_version = last_id
                else:
                    logger.info("no need to commit in {0}".format(main_dir,))
                    
                    # get last commit id
                    last_id = git.log('-1', "--format=%H", '--no-color', _cwd=main_dir, _tty_out=False).stdout.strip()
                    ap_version = last_id
            else:
                logger.info("tarfile doesn't have any files")

        response = {}
        response["ap_version"] = ap_version 
        return response
    
    def mods_dir_for_user_id(self, user_id, **kwargs):
        return os.path.join(MODMAN_GIT_ROOT, "{0}/".format(user_id,))
    
    def main_dir_for_user_id(self, user_id, **kwargs):
        return os.path.join(self.mods_dir_for_user_id(user_id,), "main/") 
        
    def git_dir_for_user_id(self, user_id, **kwargs):
        return os.path.join(self.main_dir_for_user_id(user_id), ".git")
    
    def latest_ap_version_for_user_id(self, user_id, **kwargs):
        main_dir = self.main_dir_for_user_id(user_id)
        if not os.path.exists(main_dir):
            return ''
        return git.log('-1', "--format=%H", '--no-color', _cwd=main_dir, _tty_out=False).stdout.strip()

    def ap_versions_for_user_id(self, user_id, **kwargs):
        main_dir = self.main_dir_for_user_id(user_id)
        if not os.path.exists(main_dir):
            return []
        branches = [ line.strip() for line in git.branch("--no-color", "--list", _cwd=main_dir, _tty_out=False).stdout.split() if line.strip() and line.strip() not in ("master", "*") ]
        return branches
    
    def create_repo_for_user_id(self, user_id, **kwargs):
        main_dir = self.main_dir_for_user_id(user_id)
        logger.info("using main dir {0}".format(main_dir,))
        
        #TODO some kind of locking would be good here
        # don't let it go concurrently for the same user_id
        if not os.path.exists(main_dir):
            logger.info("creating all dirs and git repo for {0}".format(main_dir,))
            os.makedirs(main_dir)
            git.init(".", _cwd=main_dir)
        else:
            logger.info("git repo is already created in {0}".format(main_dir,))
            

if __name__ == "__main__":
    logger.info("modman service starting at {0}".format(MODMAN_SERVICE_ENDPOINT))
    logger.info("git repo root at {0}".format(MODMAN_GIT_ROOT))
    server = zerorpc.Server(Service())
    server.bind(MODMAN_SERVICE_ENDPOINT)
    server.run()

