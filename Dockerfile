# Docker file to orchestrate how the result_linker is deployed.
# start from base

#Using multi stage builds
FROM node:10 as node-builder
# Copy application c
ADD . /opt/result_linker
WORKDIR /opt/result_linker/result_linker/ui

# Enable proxy for inbound traffic 
ENV http_proxy http://proxy.threatpulse.net:8080
ENV https_proxy http://proxy.threatpulse.net:8080

# Install nodejs
RUN npm config set registry http://registry.npmjs.org/ \
    # && nvm install-latest-npm \
    && npm install \
    && npm rebuild node-sass \
    && npm run build

FROM python:3.7.4

# Enable proxy for inbound traffic 
ENV http_proxy http://proxy.threatpulse.net:8080
ENV https_proxy http://proxy.threatpulse.net:8080

# Install svnlib
WORKDIR /usr/local/
RUN apt-get -y -q --force-yes install subversion
RUN  svn checkout svn://10.133.0.222/XT4210/apps/modules/svnlib --username svnuser --password svnuser --no-auth-cache --non-interactive
WORKDIR /usr/local/svnlib
RUN python setup.py bdist_wheel
RUN pip install /usr/local/svnlib/dist/*.whl
# RUN pip install svnlib

# Install dependenices
COPY requirements.txt /opt/result_linker/requirements.txt
WORKDIR /opt/result_linker
RUN bash -c "pip install --no-cache-dir -r requirements.txt"

ADD . /opt/result_linker


COPY --from=node-builder /opt/result_linker/result_linker/ui /opt/result_linker/result_linker/ui

RUN bash -c "mkdir instance"
COPY config/production.py  /opt/result_linker/instance/config.py

#RUN bash -c "python manage.py -c config.py db init"
#RUN bash -c "python manage.py -c config.py db migrate"
#RUN bash -c "python manage.py -c config.py db upgrade"
#RUN bash -c "python manage.py -c config.py add_user admin .Kuckma admin"
#RUN bash -c "python manage.py -c config.py add_user gkn start12 user"
# unset to use python-redmine auth apis
ENV http_proxy= 
ENV https_proxy= 
# expose port
EXPOSE 2323

# start app
CMD [ "python", "serve.py" ]