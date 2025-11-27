from django.contrib import admin
from .models import Project, ContactSubmission


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
