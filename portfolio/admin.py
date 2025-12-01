from django.contrib import admin
from .models import Project, ContactSubmission, IncomingIntel, BusinessMetrics


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'featured', 'order', 'created_at']
    list_filter = ['category', 'featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'featured']


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'business_name', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'business_name', 'message']
    readonly_fields = ['name', 'email', 'business_name', 'message', 'created_at']
    list_editable = ['is_read']


@admin.register(IncomingIntel)
class IncomingIntelAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'source', 'intel_type', 'status', 'created_at']
    list_filter = ['status', 'intel_type', 'source']
    search_fields = ['contact_name', 'contact_email', 'business_name', 'notes']
    list_editable = ['status']
    date_hierarchy = 'created_at'


@admin.register(BusinessMetrics)
class BusinessMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'website_visits', 'leads_generated', 'proposals_sent', 'deals_closed', 'revenue']
    list_filter = ['date']
    date_hierarchy = 'date'
