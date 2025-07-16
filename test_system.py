#!/usr/bin/env python
"""
Test script for The Shinobi Project Django system
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Set up Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shinobi_ops.settings')
django.setup()

from django.utils import timezone
from core.models import Entity, Project, Task, TimeEntry, EntityRelationship
from core.claude_integration import ClaudeBusinessIntelligence

def test_basic_functionality():
    print("🧪 TESTING SHINOBI PROJECT SYSTEM")
    print("=" * 50)
    
    # Test 1: Database connectivity
    print("\n1. 📊 Database Connectivity Test")
    print(f"   Entities: {Entity.objects.count()}")
    print(f"   Projects: {Project.objects.count()}")
    print(f"   Relationships: {EntityRelationship.objects.count()}")
    
    # Test 2: Entity relationships
    print("\n2. 🔗 Entity Relationships Test")
    shinobi = Entity.objects.get(name="The Shinobi Project")
    managed_ventures = shinobi.relationships_as_a.filter(relationship_type='manages').count()
    print(f"   Shinobi Project manages {managed_ventures} ventures")
    
    # Test 3: Create a test time entry
    print("\n3. ⏰ Time Entry Test")
    jonin = Entity.objects.get(name__contains="Jonin")
    haikutea = Entity.objects.get(name="HaikuTea")
    
    # Create a test time entry
    time_entry = TimeEntry.objects.create(
        person=jonin,
        organization=haikutea,
        start_time=timezone.now() - timedelta(hours=2),
        end_time=timezone.now() - timedelta(hours=1),
        description="Testing HaikuTea supply chain research",
        entry_method="manual",
        tracking_data={
            "test_entry": True,
            "location": "home_office",
            "tools_used": ["django", "claude_ai"]
        }
    )
    print(f"   Created time entry: {time_entry.duration_hours:.1f} hours")
    
    # Test 4: Create a test task
    print("\n4. 📋 Task Management Test")
    supply_project = Project.objects.get(name__contains="Supply Chain")
    
    task = Task.objects.create(
        title="Contact Cotswold Tea supplier",
        description="Resolve packaging issues and confirm delivery schedule",
        project=supply_project,
        assigned_to=jonin,
        status='pending',
        priority='high',
        task_data={
            "urgency": "high",
            "deadline": "august_2025",
            "contact_info": "supplier_phone_required"
        }
    )
    print(f"   Created task: {task.title}")
    
    # Test 5: Relationship queries
    print("\n5. 🕸️ Relationship Network Test")
    website_design = Entity.objects.get(name="Website Design Services")
    clients = website_design.relationships_as_a.filter(relationship_type='contractor_for')
    print(f"   Website Design has {clients.count()} client relationships")
    
    # Test 6: Project overview
    print("\n6. 📈 Project Overview Test")
    for project in Project.objects.all():
        tasks_count = project.tasks.count()
        time_entries_count = project.time_entries.count()
        print(f"   {project.name}: {tasks_count} tasks, {time_entries_count} time entries")
    
    # Test 7: Claude AI integration
    print("\n7. 🤖 Claude AI Integration Test")
    try:
        claude = ClaudeBusinessIntelligence()
        
        # Test time tracking insights
        insights = claude.generate_time_tracking_insights(jonin)
        print(f"   Time insights generated: {type(insights)}")
        
        # Test project optimization
        optimization = claude.suggest_project_optimizations(supply_project)
        print(f"   Project optimization generated: {type(optimization)}")
        
        print("   ✅ Claude AI integration working!")
        
    except Exception as e:
        print(f"   ❌ Claude AI error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 SYSTEM TEST COMPLETE")
    print("\nAdmin Interface:")
    print("- URL: http://localhost:8001/admin")
    print("- Username: admin")
    print("- Password: admin123")
    print("\nNext Steps:")
    print("1. Access admin interface to view all data")
    print("2. Create additional time entries")
    print("3. Test cross-venture analysis")
    print("4. Set up WhatsApp integration")

if __name__ == "__main__":
    test_basic_functionality()