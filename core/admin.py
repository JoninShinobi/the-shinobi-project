from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json
from .models import *

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'status', 'relationship_count', 'created_at']
    list_filter = ['entity_type', 'status', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'entity_type', 'status', 'description')
        }),
        ('Metadata (JSONB)', {
            'fields': ('metadata',),
            'classes': ('collapse',),
            'description': 'Store contact info, capabilities, preferences as JSON'
        })
    )
    
    def relationship_count(self, obj):
        count = obj.relationships_as_a.count() + obj.relationships_as_b.count()
        if count > 0:
            url = reverse('admin:core_entityrelationship_changelist') + f'?entity_a={obj.id}'
            return format_html('<a href="{}">{} relationships</a>', url, count)
        return "0 relationships"
    relationship_count.short_description = "Relationships"

@admin.register(EntityRelationship)
class EntityRelationshipAdmin(admin.ModelAdmin):
    list_display = ['entity_a', 'relationship_type', 'entity_b', 'strength', 'is_bidirectional']
    list_filter = ['relationship_type', 'strength', 'is_bidirectional', 'created_at']
    search_fields = ['entity_a__name', 'entity_b__name']
    
    fieldsets = (
        ('Relationship', {
            'fields': ('entity_a', 'relationship_type', 'entity_b', 'strength', 'is_bidirectional')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
        ('Relationship Data (JSONB)', {
            'fields': ('relationship_data',),
            'classes': ('collapse',),
            'description': 'Contract terms, shared projects, communication preferences'
        })
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary_organization', 'status', 'start_date', 'target_completion', 'task_count']
    list_filter = ['status', 'primary_organization', 'start_date']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['related_entities']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'slug', 'description', 'status')
        }),
        ('Relationships', {
            'fields': ('primary_organization', 'related_entities')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_completion', 'actual_completion')
        }),
        ('Project Data (JSONB)', {
            'fields': ('project_data',),
            'classes': ('collapse',),
            'description': 'Budget, milestones, resources, deliverables'
        })
    )
    
    def task_count(self, obj):
        count = obj.tasks.count()
        if count > 0:
            url = reverse('admin:core_task_changelist') + f'?project={obj.id}'
            return format_html('<a href="{}">{} tasks</a>', url, count)
        return "0 tasks"
    task_count.short_description = "Tasks"

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'status', 'priority', 'due_date', 'is_overdue']
    list_filter = ['status', 'priority', 'project__primary_organization', 'assigned_to']
    search_fields = ['title', 'description']
    filter_horizontal = ['related_entities']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('project', 'assigned_to', 'related_entities')
        }),
        ('Timeline', {
            'fields': ('due_date', 'estimated_hours', 'completed_at')
        }),
        ('Task Data (JSONB)', {
            'fields': ('task_data',),
            'classes': ('collapse',),
            'description': 'Instructions, dependencies, resources, notes'
        })
    )
    
    def is_overdue(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Overdue</span>')
        return "On time"
    is_overdue.short_description = "Status"

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['person', 'organization', 'project', 'start_time', 'duration_display', 'entry_method']
    list_filter = ['organization', 'entry_method', 'start_time', 'person']
    search_fields = ['person__name', 'organization__name', 'description']
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Time Entry', {
            'fields': ('person', 'organization', 'project', 'task')
        }),
        ('Time Details', {
            'fields': ('start_time', 'end_time', 'duration', 'description')
        }),
        ('Metadata', {
            'fields': ('entry_method',)
        }),
        ('Tracking Data (JSONB)', {
            'fields': ('tracking_data',),
            'classes': ('collapse',),
            'description': 'Location, tools, outcomes, WhatsApp data'
        })
    )
    
    def duration_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Active</span>')
        elif obj.duration:
            hours = obj.duration_hours
            return f"{hours:.1f}h"
        return "No duration"
    duration_display.short_description = "Duration"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'primary_entity', 'updated_at']
    list_filter = ['document_type', 'primary_entity', 'created_at']
    search_fields = ['title', 'content']
    filter_horizontal = ['related_entities']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'document_type', 'content')
        }),
        ('Relationships', {
            'fields': ('primary_entity', 'related_entities', 'related_project')
        }),
        ('File Information', {
            'fields': ('file_path',)
        }),
        ('Document Data (JSONB)', {
            'fields': ('document_data',),
            'classes': ('collapse',),
            'description': 'File info, approval status, version info, tags'
        })
    )

@admin.register(FinancialEntry)
class FinancialEntryAdmin(admin.ModelAdmin):
    list_display = ['amount_display', 'source_entity', 'target_entity', 'entry_type', 'transaction_date', 'is_paid']
    list_filter = ['entry_type', 'category', 'currency', 'transaction_date']
    search_fields = ['source_entity__name', 'target_entity__name', 'description']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Financial Information', {
            'fields': ('amount', 'currency', 'entry_type', 'category', 'description')
        }),
        ('Entities', {
            'fields': ('source_entity', 'target_entity', 'related_project')
        }),
        ('Dates', {
            'fields': ('transaction_date', 'due_date', 'paid_date')
        }),
        ('Financial Data (JSONB)', {
            'fields': ('financial_data',),
            'classes': ('collapse',),
            'description': 'Payment method, tax info, invoice details'
        })
    )
    
    def amount_display(self, obj):
        color = 'green' if obj.entry_type == 'revenue' else 'red'
        return format_html('<span style="color: {};">£{}</span>', color, obj.amount)
    amount_display.short_description = "Amount"
    
    def is_paid(self, obj):
        if obj.paid_date:
            return format_html('<span style="color: green;">Paid</span>')
        elif obj.is_overdue:
            return format_html('<span style="color: red;">Overdue</span>')
        return "Pending"
    is_paid.short_description = "Payment Status"

@admin.register(WhatsAppSession)
class WhatsAppSessionAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'entity', 'is_tracking_time', 'active_organization', 'last_activity']
    list_filter = ['is_tracking_time', 'active_organization', 'last_activity']
    search_fields = ['phone_number', 'entity__name']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('phone_number', 'entity')
        }),
        ('Active Tracking', {
            'fields': ('is_tracking_time', 'current_time_entry', 'active_organization', 'active_project')
        }),
        ('Session Data (JSONB)', {
            'fields': ('session_data',),
            'classes': ('collapse',)
        })
    )

@admin.register(ClaudeInteraction)
class ClaudeInteractionAdmin(admin.ModelAdmin):
    list_display = ['query_preview', 'interaction_type', 'entity', 'project', 'user', 'created_at']
    list_filter = ['interaction_type', 'entity', 'project', 'created_at']
    search_fields = ['query', 'response']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Context', {
            'fields': ('entity', 'project', 'user', 'interaction_type')
        }),
        ('Interaction', {
            'fields': ('query', 'response')
        }),
        ('Metadata', {
            'fields': ('interaction_data', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def query_preview(self, obj):
        return obj.query[:50] + "..." if len(obj.query) > 50 else obj.query
    query_preview.short_description = "Query"

# Custom admin site configuration
admin.site.site_header = "The Shinobi Project Operations"
admin.site.site_title = "Shinobi Ops"
admin.site.index_title = "Business Management Dashboard"
