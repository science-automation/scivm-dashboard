from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
import django.conf.urls as django_urls

from tastypie import fields
from tastypie.resources import Resource, ModelResource
from tastypie import http
from tastypie.bundle import Bundle
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse

from apikey.authentication import SciCloudApiKeyAuthentication
from jobs.jids import JIDS

from cloud.util.zip_packer import Packer, UnPacker

import json
import pickle
import logging
import functools

logger = logging.getLogger("dummy")


def dispatch(path="", methods=("POST",)):
    """ You can resgister your extra handlers using this decorator.
        
        class MyResource(CloudResourceMixin, SomeResourceClass):
            
            @dispatch("/path/without/api/version/resource/prefix/(?<pk>\w+)/", methods=("POST",))
            def my_stuff_hnd(self, request, pk, **kwargs):
                # handler code
        
        Handlers must be postfixed with "_hnd".
        If you don't specify path it will build one from the name of the function.
        
        @dispatch
        def add_item_hnd(..)  ->  /<api>/<version>/<resource_name>/add/item/
    """

    def wrapper0(f):
        @functools.wraps(f)    
        def wrapper(self, request, **kwargs):
            return self.dispatch_cloud(f, request, **kwargs)
        
        wrapper.dispatched = True
        wrapper.path = path
        wrapper.methods = methods
        
        return wrapper
    
    if callable(path):
        f = path
        path = "/".join(f.func_name[:-4].split("_"))
        return wrapper0(f)
    
    return wrapper0


class CloudResourceMixin(object):
    """ Helper. Use with your resource class. 
        See CloudResource, CloudModelResource below.
        
        Features:

        *   @dispatch decorator support
        *   logs incoming data if settings.DEBUG=True
        *   json file unpacker 
        *   jids file unpacker

    """
    
    def load_json_from_file(self, request, name):
        """ Try to load json object from request.FILES[<name>] """
        if name not in request.FILES:
            logger.debug("file is missing: %s" % name)
            raise ValidationError("%s is required" % name)
        
        try:
            raw = UnPacker(request.FILES[name]).next()
            return json.loads(raw)
        except Exception, e:
            logger.debug("cannot load json in %s: %s" % (name, str(e)))
            raise ValidationError("%s cannot be parsed" % name)
    
    def load_jids_from_file(self, request, name):
        """ Try to load jids object from request.FILES[<name>] """
        jids_desc = self.load_json_from_file(request, name)
        try:
            return JIDS(jids_desc)
        except Exception, e:
            logger.debug("jids descriptor is invalid in %s: %s %s" % (name, str(jids_desc)), str(e))
            raise ValidationError("%s is invalid" % name)
    
    def dispatch_cloud(self, method, request, **kwargs):
        """
        Handles the common operations (allowed HTTP method, authentication,
        throttling, method lookup) surrounding most CRUD interactions.
        """
        
        if 'HTTP_X_HTTP_METHOD_OVERRIDE' in request.META:
            request.method = request.META['HTTP_X_HTTP_METHOD_OVERRIDE']

        self.is_authenticated(request)
        self.throttle_check(request)

        # All clear. Process the request.
        # request = convert_post_to_put(request)
        
        if settings.DEBUG:
            self.log_request_info(request, **kwargs)
            self.log_incoming_files(request, **kwargs)

        response = method(self, request, **kwargs)

        # Add the throttled request.
        self.log_throttled_access(request)

        # If what comes back isn't a ``HttpResponse``, assume that the
        # request was accepted and that some action occurred. This also
        # prevents Django from freaking out.
        if not isinstance(response, HttpResponse):
            return http.HttpNoContent()

        return response
    
    def log_incoming_files(self, request, **kwargs):
        logger.debug("FILES")
        for name, f in request.FILES.items():
            logger.debug("    ->filename: '{name}'".format(name=name))
            errors = []
            try:
                for i, part in enumerate(UnPacker(f)):
                    try:
                        lets_try = pickle.loads(part)
                        logger.debug("    ({i}) gz/pickle {data}".format(i=i, data=lets_try))
                        continue
                    except Exception, e:
                        errors.append(e)
                    try:
                        data = json.loads(part)
                        logger.debug("    ({i}) gz/json {data}".format(i=i, data=data))
                        continue
                    except Exception, e:
                        errors.append(e)
                        logger.debug("    ({i}) gz/unknown len:{l}".format(i=i, l=len(part)))
                        #for e in errors:
                        #    print e
            except:
                logger.debug("    some binary file - dont know how to unpack")
            f.seek(0)
        logger.debug("")
         
    def log_request_info(self, request, **kwargs):
        logger.debug("--------------------------------------------")
        logger.debug("REQUEST   {path}".format(path=request.path))
        logger.debug("METHOD    {method}".format(method=request.method))
        logger.debug("HANDLER   {self}".format(self=self.__class__)) 
            
        if request.GET:
            logger.debug("URLARGS")
            for k,v in request.GET.items():
                logger.debug("    {k}: {v}".format(k=k, v=v))
            logger.debug("")
            
        if request.POST: 
            logger.debug("POSTDATA")
            for k,v in request.POST.items():
                logger.debug("    {k}: {v}".format(k=k, v=v))
            logger.debug("")
        
    def prepend_urls(self):
        """ Generate url entries for handlers """
        endpoint_methods = [ getattr(self, attr_name) for attr_name in dir(self) if attr_name.endswith("_hnd")]
        url_data = [ (e.func_name, e.path) for e in endpoint_methods ]
        urls = [ self._url_for_dispatched_method(func_name, path) for func_name, path in url_data ]
        return urls

    def _url_for_dispatched_method(self, attr_name, path):
        """ Generate url entry for handler name and path. """
        rn = self._meta.resource_name
        if not path.startswith("/"):
            path = "/" + path
        if not path.endswith("/"):
            path = path + "/"
        url = django_urls.url(r"^(?P<resource_name>%s)%s$" % (rn, path), 
                self.wrap_view('%s' % attr_name), 
                name="cloudapi-%s-%s" % (rn, attr_name.replace("_","-")[:-4]),
        ) 
        # logger.info("cloudapi pattern registered: %s" % url)
        return url
    
    def raise_response(self, request, data, response_class=http.HttpResponse):
        raise ImmediateHttpResponse(self.error_response(request, data, response_class=response_class))


class CloudResource(CloudResourceMixin, Resource):
    """ Our tastypie.Resource extension """
    pass


class CloudModelResource(CloudResourceMixin, ModelResource):
    """ Our tastypie.ModelResource extension """
    pass
