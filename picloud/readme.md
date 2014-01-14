Temporary scicloud api endpoints
================================

This is a toy system which helps us to understand all the tricks of the original picloud api.
Going to be fully rewritten and separated from the dashboard.

We use parts of tastypie now, a custom made system will fit the purpose better.


services (backends dir)
-----------------------

See backends/conf.py for configuration options.

*	modman_service.py
	
	zerorpc service; manages uploaded modules and ap_versions


