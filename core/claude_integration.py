"""
Claude AI integration for The Shinobi Project operations
"""

import os
import json
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from anthropic import Anthropic
from .models import ClaudeInteraction, Entity, Project


class ClaudeBusinessIntelligence:
    """
    Claude AI integration for business intelligence and analysis
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.CLAUDE_API_KEY)
    
    def analyze_business_performance(self, entity: Optional[Entity] = None, 
                                   project: Optional[Project] = None) -> Dict[str, Any]:
        """
        Analyze business performance across ventures or for specific entity/project
        """
        context = self._build_context(entity, project)
        
        prompt = f"""
        Analyze the business performance for The Shinobi Project based on the following data:
        
        {context}
        
        Please provide:
        1. Key performance insights
        2. Recommendations for improvement
        3. Risk analysis
        4. Opportunities for growth
        5. Cross-venture synergies
        
        Format your response as JSON with these sections.
        """
        
        response = self._query_claude(prompt, 'business_analysis', entity, project)
        return self._parse_response(response)
    
    def generate_time_tracking_insights(self, entity: Entity) -> Dict[str, Any]:
        """
        Generate insights from time tracking data
        """
        from .models import TimeEntry
        
        time_entries = TimeEntry.objects.filter(person=entity).order_by('-start_time')[:50]
        
        context = {
            'entity': entity.name,
            'recent_entries': [
                {
                    'organization': entry.organization.name if entry.organization else 'General',
                    'duration_hours': entry.duration_hours,
                    'description': entry.description,
                    'date': entry.start_time.date().isoformat(),
                    'entry_method': entry.entry_method
                }
                for entry in time_entries
            ]
        }
        
        prompt = f"""
        Analyze time tracking patterns for {entity.name} based on this data:
        
        {json.dumps(context, indent=2)}
        
        Provide insights on:
        1. Time allocation patterns
        2. Productivity trends
        3. Work-life balance
        4. Recommendations for optimization
        
        Format as JSON.
        """
        
        response = self._query_claude(prompt, 'time_analysis', entity)
        return self._parse_response(response)
    
    def suggest_project_optimizations(self, project: Project) -> Dict[str, Any]:
        """
        Suggest optimizations for a specific project
        """
        context = {
            'project': project.name,
            'organization': project.primary_organization.name,
            'status': project.status,
            'description': project.description,
            'project_data': project.project_data,
            'tasks': [
                {
                    'title': task.title,
                    'status': task.status,
                    'priority': task.priority,
                    'assigned_to': task.assigned_to.name if task.assigned_to else None
                }
                for task in project.tasks.all()
            ],
            'time_entries': [
                {
                    'person': entry.person.name,
                    'duration_hours': entry.duration_hours,
                    'description': entry.description
                }
                for entry in project.time_entries.all()
            ]
        }
        
        prompt = f"""
        Analyze this project and suggest optimizations:
        
        {json.dumps(context, indent=2)}
        
        Provide:
        1. Current status assessment
        2. Bottleneck identification
        3. Resource optimization suggestions
        4. Timeline recommendations
        5. Risk mitigation strategies
        
        Format as JSON.
        """
        
        response = self._query_claude(prompt, 'project_optimization', project=project)
        return self._parse_response(response)
    
    def generate_cross_venture_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive cross-venture analysis report
        """
        from .models import EntityRelationship, TimeEntry, FinancialEntry
        
        context = {
            'organizations': [
                {
                    'name': org.name,
                    'type': org.entity_type,
                    'metadata': org.metadata,
                    'relationships': org.relationships_as_a.count() + org.relationships_as_b.count()
                }
                for org in Entity.objects.filter(entity_type='organization')
            ],
            'recent_time_entries': [
                {
                    'person': entry.person.name,
                    'organization': entry.organization.name if entry.organization else 'General',
                    'duration_hours': entry.duration_hours,
                    'date': entry.start_time.date().isoformat()
                }
                for entry in TimeEntry.objects.order_by('-start_time')[:20]
            ],
            'relationships': [
                {
                    'entity_a': rel.entity_a.name,
                    'relationship_type': rel.relationship_type,
                    'entity_b': rel.entity_b.name,
                    'strength': rel.strength
                }
                for rel in EntityRelationship.objects.all()
            ]
        }
        
        prompt = f"""
        Generate a comprehensive cross-venture analysis report for The Shinobi Project:
        
        {json.dumps(context, indent=2)}
        
        Provide:
        1. Executive summary
        2. Venture performance comparison
        3. Resource allocation analysis
        4. Relationship network insights
        5. Strategic recommendations
        6. Growth opportunities
        
        Format as JSON with clear sections.
        """
        
        response = self._query_claude(prompt, 'cross_venture_report')
        return self._parse_response(response)
    
    def _build_context(self, entity: Optional[Entity], project: Optional[Project]) -> str:
        """
        Build context string for Claude queries
        """
        from .models import TimeEntry, FinancialEntry, Task
        
        context = {
            'timestamp': timezone.now().isoformat(),
            'scope': {}
        }
        
        if entity:
            context['scope']['entity'] = {
                'name': entity.name,
                'type': entity.entity_type,
                'metadata': entity.metadata
            }
        
        if project:
            context['scope']['project'] = {
                'name': project.name,
                'status': project.status,
                'description': project.description,
                'project_data': project.project_data
            }
        
        return json.dumps(context, indent=2)
    
    def _query_claude(self, prompt: str, interaction_type: str, 
                     entity: Optional[Entity] = None, 
                     project: Optional[Project] = None) -> str:
        """
        Query Claude API and log the interaction
        """
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response = message.content[0].text
            
            # Log the interaction
            ClaudeInteraction.objects.create(
                entity=entity,
                project=project,
                query=prompt,
                response=response,
                interaction_type=interaction_type,
                interaction_data={
                    'model': "claude-3-5-sonnet-20241022",
                    'tokens_used': message.usage.input_tokens + message.usage.output_tokens,
                    'temperature': 0.3
                }
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Claude API Error: {str(e)}"
            
            # Log the error
            ClaudeInteraction.objects.create(
                entity=entity,
                project=project,
                query=prompt,
                response=error_msg,
                interaction_type=f"{interaction_type}_error",
                interaction_data={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            
            return error_msg
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Claude's response, handling both JSON and text responses
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # If not JSON, return as structured text
            return {
                'analysis': response,
                'format': 'text',
                'timestamp': timezone.now().isoformat()
            }


# Convenience functions for easy use
def analyze_business_performance(entity_name: str = None, project_name: str = None):
    """
    Quick business performance analysis
    """
    claude = ClaudeBusinessIntelligence()
    
    entity = None
    project = None
    
    if entity_name:
        entity = Entity.objects.filter(name__icontains=entity_name).first()
    
    if project_name:
        project = Project.objects.filter(name__icontains=project_name).first()
    
    return claude.analyze_business_performance(entity, project)


def get_time_insights(person_name: str):
    """
    Get time tracking insights for a person
    """
    claude = ClaudeBusinessIntelligence()
    
    person = Entity.objects.filter(
        name__icontains=person_name,
        entity_type='individual'
    ).first()
    
    if not person:
        return {"error": f"Person '{person_name}' not found"}
    
    return claude.generate_time_tracking_insights(person)


def optimize_project(project_name: str):
    """
    Get optimization suggestions for a project
    """
    claude = ClaudeBusinessIntelligence()
    
    project = Project.objects.filter(name__icontains=project_name).first()
    
    if not project:
        return {"error": f"Project '{project_name}' not found"}
    
    return claude.suggest_project_optimizations(project)


def generate_dashboard_insights():
    """
    Generate insights for the management dashboard
    """
    claude = ClaudeBusinessIntelligence()
    return claude.generate_cross_venture_report()