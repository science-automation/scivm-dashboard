
# Quickstart
Use the [Quickstart](https://github.com/science-automation/wiki/QuickStart) to get
started.
(Quickstart coming soon)

# Help
To report issues please use [Github](https://github.com/science-automation/scivm-dashboard/issues)

# Dev Setup
Science VM needs Redis for caching and queueing.  By default, it assumes Redis
is running on localhost.

* `pip install -r requirements.txt`
* `python manage.py syncdb --noinput`
* `python manage.py migrate`
* `python manage.py createsuperuser`
* `python manage.py runserver`
* `python manage.py celery worker -B --scheduler=djcelery.schedulers.DatabaseScheduler -E` (in another terminal)
*  Open browser to http://localhost:8000


Alternate dev setup using vagrant (this will install all dependencies including
docker itself for a self-contained dev environment):

* `vagrant up`
* `vagrant ssh`
* `python manage.py syncdb --noinput`
* `python manage.py migrate`
* `python manage.py createsuperuser`
* `./manage.py runserver 0.0.0.0:8000`
* `./manage.py celery worker -B --scheduler=djcelery.schedulers.DatabaseScheduler -E` (in separate ssh session)
* Open browser to http://localhost:8000

# Scicloud API
These extra steps needed to be able to use the scicloud api:

* `python manage.py celery worker -E -P gevent -c 1000`
* `python manage.py consume_job_results`
* `python picloud/backends/modman_service.py` # see more in picloud/backends/conf.py

# Screenshots

![Jobs](https://www.scivm.com/sciencevm.png)

