FROM ubuntu:12.04
MAINTAINER Science Automation "http://www.scivm.com"
RUN echo "deb ftp://mirror.hetzner.de/ubuntu/packages precise main restricted universe multiverse" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

# base software
run apt-get install -y python-dev python-setuptools python-software-properties libxml2-dev libxslt-dev libmysqlclient-dev supervisor redis-server git-core wget make g++ libreadline-dev libncurses5-dev libpcre3-dev  libpq-dev libmysqlclient-dev dialog net-tools lynx vim-tiny nano openssh-server git curl

# ssh server
RUN apt-get -y install openssh-server
RUN mkdir -p /var/run/sshd
RUN locale-gen en_US en_US.UTF-8

# nginx
RUN add-apt-repository -y ppa:nginx/stable
RUN apt-get update
RUN apt-get -y install nginx

env SCIVM_APP_DIR /opt/apps/scivm-dashboard
env SCIVM_VE_DIR /opt/ve/scivm-dashboard
run easy_install pip
run pip install setuptools --no-use-wheel --upgrade
run pip install virtualenv
run pip install uwsgi
run mkdir -p /opt/apps; cd /opt/apps; git clone https://github.com/science-automation/scivm-dashboard.git
run virtualenv --no-site-packages $SCIVM_VE_DIR
run $SCIVM_VE_DIR/bin/pip install MySQL-Python==1.2.3
run $SCIVM_VE_DIR/bin/pip install psycopg2
run (find $SCIVM_APP_DIR -name "*.db" -delete)
run $SCIVM_VE_DIR/bin/pip install -r $SCIVM_APP_DIR/requirements.txt

VOLUME /var/log/scivm-dashboard
EXPOSE 22
EXPOSE 80
EXPOSE 443
EXPOSE 6379
EXPOSE 5000
CMD ["/bin/sh", "-e", "/opt/apps/scivm-dashboard/.docker/run.sh"]
