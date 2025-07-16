from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from core.models import (
    Entity, EntityType, EntityRelationship, Project, ProjectStatus,
    Task, TaskStatus, TimeEntry, FinancialEntry, Document
)
from core.claude_integration import ClaudeBusinessIntelligence

def dashboard_view(request):
    """
    Dynamic dashboard that adapts to different entity types and data
    """
    # Get filter parameters
    entity_id = request.GET.get('entity_id')
    view_type = request.GET.get('view', 'overview')  # overview, entity, project, time, finance
    
    context = {
        'entities': Entity.objects.all().order_by('name'),
        'organizations': Entity.objects.filter(entity_type=EntityType.ORGANIZATION),
        'individuals': Entity.objects.filter(entity_type=EntityType.INDIVIDUAL),
        'view_type': view_type,
        'selected_entity_id': entity_id
    }
    
    if entity_id:
        entity = get_object_or_404(Entity, id=entity_id)
        context.update(get_entity_dashboard_data(entity))
    else:
        context.update(get_overview_dashboard_data())
    
    return render(request, 'reporting/simple_dashboard.html', context)

def get_overview_dashboard_data():
    """
    Get data for the main overview dashboard
    """
    return {
        'total_entities': Entity.objects.count(),
        'total_organizations': Entity.objects.filter(entity_type=EntityType.ORGANIZATION).count(),
        'total_individuals': Entity.objects.filter(entity_type=EntityType.INDIVIDUAL).count(),
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status=ProjectStatus.ACTIVE).count(),
        'total_tasks': Task.objects.count(),
        'pending_tasks': Task.objects.filter(status=TaskStatus.PENDING).count(),
        'total_time_entries': TimeEntry.objects.count(),
        'total_relationships': EntityRelationship.objects.count(),
        
        # Recent activity
        'recent_time_entries': TimeEntry.objects.order_by('-created_at')[:5],
        'recent_tasks': Task.objects.order_by('-created_at')[:5],
        'urgent_tasks': Task.objects.filter(priority='urgent').order_by('-created_at')[:5],
        
        # Top organizations by activity
        'top_organizations': Entity.objects.filter(
            entity_type=EntityType.ORGANIZATION
        ).annotate(
            time_entries_count=Count('organization_time_entries'),
            projects_count=Count('primary_projects')
        ).order_by('-time_entries_count')[:5],
        
        # Chart data
        'entity_distribution': get_entity_distribution_data(),
        'project_status_distribution': get_project_status_data(),
        'time_tracking_trends': get_time_tracking_trends(),
        'relationship_network': get_relationship_network_data(),
    }

def get_entity_dashboard_data(entity):
    """
    Get data for a specific entity dashboard
    """
    # Base data
    data = {
        'entity': entity,
        'entity_type_display': entity.get_entity_type_display(),
        'metadata': entity.metadata,
    }
    
    # Relationships
    relationships_as_a = entity.relationships_as_a.all()
    relationships_as_b = entity.relationships_as_b.all()
    data['relationships'] = {
        'outgoing': relationships_as_a,
        'incoming': relationships_as_b,
        'total': relationships_as_a.count() + relationships_as_b.count(),
        'types': get_relationship_types_data(entity),
    }
    
    # Different data based on entity type
    if entity.entity_type == EntityType.ORGANIZATION:
        data.update(get_organization_data(entity))
    elif entity.entity_type == EntityType.INDIVIDUAL:
        data.update(get_individual_data(entity))
    else:
        data.update(get_external_entity_data(entity))
    
    return data

def get_organization_data(entity):
    """
    Get data specific to organization entities
    """
    return {
        'primary_projects': entity.primary_projects.all(),
        'involved_projects': entity.involved_projects.all(),
        'time_entries': entity.organization_time_entries.all()[:10],
        'total_time_hours': sum([entry.duration for entry in entity.organization_time_entries.all() if entry.duration], timedelta(0)),
        'assigned_tasks': entity.assigned_tasks.all()[:10],
        'documents': entity.primary_documents.all()[:5],
        'financial_incoming': entity.incoming_finances.all()[:5],
        'financial_outgoing': entity.outgoing_finances.all()[:5],
        
        # Charts
        'time_distribution': get_time_distribution_data(entity),
        'project_timeline': get_project_timeline_data(entity),
        'task_priority_breakdown': get_task_priority_data(entity),
    }

def get_individual_data(entity):
    """
    Get data specific to individual entities
    """
    return {
        'time_entries': entity.person_time_entries.all()[:10],
        'assigned_tasks': entity.assigned_tasks.all()[:10],
        'total_time_hours': sum([entry.duration for entry in entity.person_time_entries.all() if entry.duration], timedelta(0)),
        'organizations_worked': entity.person_time_entries.values(
            'organization__name'
        ).annotate(
            hours=Sum('duration')
        ).order_by('-hours'),
        
        # Charts
        'time_by_organization': get_time_by_organization_data(entity),
        'productivity_trends': get_productivity_trends_data(entity),
        'task_completion_rate': get_task_completion_data(entity),
    }

def get_external_entity_data(entity):
    """
    Get data for external entities (suppliers, partners, etc.)
    """
    return {
        'documents': entity.primary_documents.all()[:5],
        'financial_transactions': (
            list(entity.incoming_finances.all()[:5]) + 
            list(entity.outgoing_finances.all()[:5])
        ),
        'interaction_history': get_interaction_history(entity),
    }

# Chart data functions
def get_entity_distribution_data():
    """
    Get data for entity type distribution chart
    """
    return Entity.objects.values('entity_type').annotate(
        count=Count('id')
    ).order_by('entity_type')

def get_project_status_data():
    """
    Get data for project status distribution
    """
    return Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

def get_time_tracking_trends():
    """
    Get time tracking trends over last 30 days
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Group by day
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_entries = TimeEntry.objects.filter(
            start_time__date=current_date
        ).aggregate(
            total_hours=Sum('duration')
        )['total_hours'] or timedelta(0)
        
        daily_data.append({
            'date': current_date.isoformat(),
            'hours': day_entries.total_seconds() / 3600 if day_entries else 0
        })
        
        current_date += timedelta(days=1)
    
    return daily_data

def get_relationship_network_data():
    """
    Get data for relationship network visualization
    """
    nodes = []
    edges = []
    
    # Add nodes (entities)
    for entity in Entity.objects.all():
        nodes.append({
            'id': str(entity.id),
            'name': entity.name,
            'type': entity.entity_type,
            'group': entity.entity_type
        })
    
    # Add edges (relationships)
    for rel in EntityRelationship.objects.all():
        edges.append({
            'source': str(rel.entity_a.id),
            'target': str(rel.entity_b.id),
            'type': rel.relationship_type,
            'strength': rel.strength
        })
    
    return {
        'nodes': nodes,
        'edges': edges
    }

def get_time_distribution_data(entity):
    """
    Get time distribution data for an organization
    """
    time_data = []
    for entry in entity.organization_time_entries.all():
        if entry.person and entry.duration:
            time_data.append({
                'person__name': entry.person.name,
                'total_hours': entry.duration.total_seconds() / 3600
            })
    
    # Group by person and sum hours
    person_hours = {}
    for item in time_data:
        name = item['person__name']
        if name not in person_hours:
            person_hours[name] = 0
        person_hours[name] += item['total_hours']
    
    return [{'person__name': name, 'total_hours': hours} for name, hours in person_hours.items()]

def get_project_timeline_data(entity):
    """
    Get project timeline data for visualization
    """
    projects = entity.primary_projects.all()
    timeline_data = []
    
    for project in projects:
        timeline_data.append({
            'name': project.name,
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'target_completion': project.target_completion.isoformat() if project.target_completion else None,
            'actual_completion': project.actual_completion.isoformat() if project.actual_completion else None,
            'status': project.status,
            'progress': calculate_project_progress(project)
        })
    
    return timeline_data

def calculate_project_progress(project):
    """
    Calculate project progress based on completed tasks
    """
    total_tasks = project.tasks.count()
    if total_tasks == 0:
        return 0
    
    completed_tasks = project.tasks.filter(status=TaskStatus.COMPLETED).count()
    return round((completed_tasks / total_tasks) * 100, 1)

def get_task_priority_data(entity):
    """
    Get task priority breakdown
    """
    return entity.assigned_tasks.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

def get_time_by_organization_data(person):
    """
    Get time allocation by organization for an individual
    """
    org_hours = {}
    for entry in person.person_time_entries.all():
        if entry.organization and entry.duration:
            org_name = entry.organization.name
            if org_name not in org_hours:
                org_hours[org_name] = 0
            org_hours[org_name] += entry.duration.total_seconds() / 3600
    
    return [{'organization__name': name, 'total_hours': hours} for name, hours in org_hours.items()]

def get_productivity_trends_data(person):
    """
    Get productivity trends for an individual
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=14)
    
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_entries = person.person_time_entries.filter(
            start_time__date=current_date
        ).aggregate(
            total_hours=Sum('duration')
        )['total_hours'] or timedelta(0)
        
        daily_data.append({
            'date': current_date.isoformat(),
            'hours': day_entries.total_seconds() / 3600 if day_entries else 0
        })
        
        current_date += timedelta(days=1)
    
    return daily_data

def get_task_completion_data(person):
    """
    Get task completion rate for an individual
    """
    total_tasks = person.assigned_tasks.count()
    if total_tasks == 0:
        return 0
    
    completed_tasks = person.assigned_tasks.filter(status=TaskStatus.COMPLETED).count()
    return round((completed_tasks / total_tasks) * 100, 1)

def get_relationship_types_data(entity):
    """
    Get relationship types distribution for an entity
    """
    outgoing = entity.relationships_as_a.values('relationship_type').annotate(
        count=Count('id')
    )
    incoming = entity.relationships_as_b.values('relationship_type').annotate(
        count=Count('id')
    )
    
    return {
        'outgoing': list(outgoing),
        'incoming': list(incoming)
    }

def get_interaction_history(entity):
    """
    Get interaction history for external entities
    """
    # This would include documents, financial transactions, etc.
    return {
        'documents': entity.primary_documents.count(),
        'financial_transactions': (
            entity.incoming_finances.count() + 
            entity.outgoing_finances.count()
        ),
        'last_interaction': entity.updated_at
    }

# AJAX endpoints for dynamic updates
def get_entity_data_json(request, entity_id):
    """
    Get entity data as JSON for AJAX updates
    """
    entity = get_object_or_404(Entity, id=entity_id)
    data = get_entity_dashboard_data(entity)
    
    # Convert model instances to dictionaries for JSON
    # This is a simplified version - you'd need to serialize properly
    return JsonResponse({
        'entity_name': entity.name,
        'entity_type': entity.entity_type,
        'relationships_count': data['relationships']['total'],
        'metadata': entity.metadata,
    })

def get_ai_insights_json(request, entity_id=None):
    """
    Get AI insights for an entity via AJAX
    """
    try:
        claude = ClaudeBusinessIntelligence()
        
        if entity_id:
            entity = get_object_or_404(Entity, id=entity_id)
            insights = claude.analyze_business_performance(entity)
        else:
            # Overview insights
            insights = claude.analyze_business_network()
        
        return JsonResponse({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def get_charts_data_json(request):
    """
    Get chart data for dashboard updates
    """
    chart_type = request.GET.get('type', 'overview')
    entity_id = request.GET.get('entity_id')
    
    if entity_id:
        entity = get_object_or_404(Entity, id=entity_id)
        if chart_type == 'time_distribution':
            data = get_time_distribution_data(entity)
        elif chart_type == 'project_timeline':
            data = get_project_timeline_data(entity)
        else:
            data = {}
    else:
        if chart_type == 'entity_distribution':
            data = list(get_entity_distribution_data())
        elif chart_type == 'time_trends':
            data = get_time_tracking_trends()
        elif chart_type == 'relationship_network':
            data = get_relationship_network_data()
        else:
            data = {}
    
    return JsonResponse(data, safe=False)
