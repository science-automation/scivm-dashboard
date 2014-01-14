from django.contrib import admin
from .models import Job, JobGroup


class JobAdmin(admin.ModelAdmin):
    
    def get_query_set(self):
        # show __all__ objects
        qs = Job.allobjects
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class JobGroupAdmin(admin.ModelAdmin):
    
    def get_query_set(self):
        # show __all__ objects
        qs = JobGroup.allobjects
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.register(Job, JobAdmin)
admin.site.register(JobGroup, JobGroupAdmin)
