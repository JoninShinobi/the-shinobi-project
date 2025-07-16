#!/usr/bin/env python
"""
Create sample data for dashboard testing
"""
import os
import sys
import django
from datetime import datetime, timedelta
from random import randint, choice

# Set up Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shinobi_ops.settings')
django.setup()

from django.utils import timezone
from core.models import Entity, TimeEntry, Task, Project, FinancialEntry, Document
from core.models import TaskStatus, TaskPriority, FinancialEntryType, DocumentType

def create_sample_data():
    print("🎨 Creating sample data for dashboard visualization...")
    
    # Get entities
    jonin = Entity.objects.get(name__contains="Jonin")
    haikutea = Entity.objects.get(name="HaikuTea")
    aaron_isaac = Entity.objects.get(name="Aaron Isaac")
    birdman = Entity.objects.get(name="Birdman Tutoring")
    website_design = Entity.objects.get(name="Website Design Services")
    soundbox = Entity.objects.get(name="SoundBox")
    
    # Get projects
    haikutea_project = Project.objects.get(name__contains="Supply Chain")
    carol_project = Project.objects.get(name__contains="Carol Leeming")
    django_project = Project.objects.get(name__contains="Django")
    
    # Create time entries for the last 30 days
    print("⏰ Creating time entries...")
    time_entries_data = [
        # HaikuTea work
        {"days_ago": 1, "hours": 3, "org": haikutea, "desc": "Researching new tea suppliers"},
        {"days_ago": 2, "hours": 2, "org": haikutea, "desc": "Updating website product descriptions"},
        {"days_ago": 3, "hours": 4, "org": haikutea, "desc": "Meeting with Mike about investment"},
        {"days_ago": 5, "hours": 1.5, "org": haikutea, "desc": "Packaging design review"},
        {"days_ago": 7, "hours": 2.5, "org": haikutea, "desc": "Supply chain optimization"},
        {"days_ago": 10, "hours": 3, "org": haikutea, "desc": "Poetry selection for new blends"},
        {"days_ago": 12, "hours": 2, "org": haikutea, "desc": "Customer feedback analysis"},
        {"days_ago": 15, "hours": 4, "org": haikutea, "desc": "Supplier negotiations"},
        {"days_ago": 18, "hours": 1, "org": haikutea, "desc": "Website maintenance"},
        {"days_ago": 20, "hours": 3, "org": haikutea, "desc": "Product photography"},
        
        # Aaron Isaac creative work
        {"days_ago": 1, "hours": 2, "org": aaron_isaac, "desc": "Writing new poetry collection"},
        {"days_ago": 3, "hours": 1.5, "org": aaron_isaac, "desc": "Editing published works"},
        {"days_ago": 4, "hours": 3, "org": aaron_isaac, "desc": "Performance preparation"},
        {"days_ago": 6, "hours": 2, "org": aaron_isaac, "desc": "Linklings CIC collaboration"},
        {"days_ago": 8, "hours": 1, "org": aaron_isaac, "desc": "Social media content creation"},
        {"days_ago": 11, "hours": 2.5, "org": aaron_isaac, "desc": "Poetry workshop planning"},
        {"days_ago": 14, "hours": 3, "org": aaron_isaac, "desc": "Creative writing session"},
        {"days_ago": 16, "hours": 1.5, "org": aaron_isaac, "desc": "Book promotion activities"},
        {"days_ago": 19, "hours": 2, "org": aaron_isaac, "desc": "Manuscript review"},
        {"days_ago": 22, "hours": 4, "org": aaron_isaac, "desc": "Poetry reading preparation"},
        
        # Birdman Tutoring
        {"days_ago": 2, "hours": 1, "org": birdman, "desc": "Guitar lesson with Elias"},
        {"days_ago": 4, "hours": 2, "org": birdman, "desc": "Lesson planning and curriculum"},
        {"days_ago": 7, "hours": 1.5, "org": birdman, "desc": "LMS development planning"},
        {"days_ago": 9, "hours": 1, "org": birdman, "desc": "Guitar lesson with Elias"},
        {"days_ago": 11, "hours": 2, "org": birdman, "desc": "Teaching materials preparation"},
        {"days_ago": 16, "hours": 1, "org": birdman, "desc": "Guitar lesson with Elias"},
        {"days_ago": 18, "hours": 1.5, "org": birdman, "desc": "Student progress assessment"},
        {"days_ago": 23, "hours": 1, "org": birdman, "desc": "Guitar lesson with Elias"},
        {"days_ago": 25, "hours": 2, "org": birdman, "desc": "Music theory preparation"},
        
        # Website Design work
        {"days_ago": 1, "hours": 4, "org": website_design, "desc": "Carol Leeming website development"},
        {"days_ago": 3, "hours": 3, "org": website_design, "desc": "Django model optimization"},
        {"days_ago": 5, "hours": 2, "org": website_design, "desc": "Client consultation"},
        {"days_ago": 8, "hours": 5, "org": website_design, "desc": "Database design and implementation"},
        {"days_ago": 10, "hours": 3, "org": website_design, "desc": "Frontend development"},
        {"days_ago": 13, "hours": 4, "org": website_design, "desc": "API integration"},
        {"days_ago": 15, "hours": 2, "org": website_design, "desc": "Testing and debugging"},
        {"days_ago": 17, "hours": 3, "org": website_design, "desc": "Deployment preparation"},
        {"days_ago": 21, "hours": 2, "org": website_design, "desc": "Project planning"},
        {"days_ago": 24, "hours": 3, "org": website_design, "desc": "Technical research"},
        
        # SoundBox work
        {"days_ago": 2, "hours": 2, "org": soundbox, "desc": "Event planning platform design"},
        {"days_ago": 6, "hours": 1.5, "org": soundbox, "desc": "Community outreach"},
        {"days_ago": 9, "hours": 3, "org": soundbox, "desc": "Django development"},
        {"days_ago": 13, "hours": 2, "org": soundbox, "desc": "Music venue research"},
        {"days_ago": 17, "hours": 1, "org": soundbox, "desc": "Partnership discussions"},
        {"days_ago": 20, "hours": 2.5, "org": soundbox, "desc": "Event coordination system"},
        {"days_ago": 26, "hours": 3, "org": soundbox, "desc": "Cultural advocacy planning"},
    ]
    
    created_entries = 0
    for entry_data in time_entries_data:
        start_time = timezone.now() - timedelta(days=entry_data["days_ago"])
        end_time = start_time + timedelta(hours=entry_data["hours"])
        
        TimeEntry.objects.create(
            person=jonin,
            organization=entry_data["org"],
            start_time=start_time,
            end_time=end_time,
            description=entry_data["desc"],
            entry_method="manual",
            tracking_data={
                "location": "home_office",
                "productivity_rating": randint(7, 10),
                "sample_data": True
            }
        )
        created_entries += 1
    
    print(f"✅ Created {created_entries} time entries")
    
    # Create tasks
    print("📋 Creating tasks...")
    tasks_data = [
        # HaikuTea tasks
        {"title": "Finalize Cotswold Tea contract", "project": haikutea_project, "priority": "urgent", "status": "pending"},
        {"title": "Design autumn tea packaging", "project": haikutea_project, "priority": "high", "status": "in_progress"},
        {"title": "Write poetry for winter blend", "project": haikutea_project, "priority": "medium", "status": "pending"},
        {"title": "Update website inventory system", "project": haikutea_project, "priority": "medium", "status": "completed"},
        {"title": "Research subscription service options", "project": haikutea_project, "priority": "low", "status": "pending"},
        
        # Carol Leeming website tasks
        {"title": "Complete poetry showcase section", "project": carol_project, "priority": "high", "status": "in_progress"},
        {"title": "Implement CMS functionality", "project": carol_project, "priority": "high", "status": "pending"},
        {"title": "Design responsive mobile layout", "project": carol_project, "priority": "medium", "status": "completed"},
        {"title": "Set up hosting and domain", "project": carol_project, "priority": "medium", "status": "pending"},
        {"title": "Create admin dashboard", "project": carol_project, "priority": "low", "status": "pending"},
        
        # Django system tasks
        {"title": "Implement WhatsApp integration", "project": django_project, "priority": "high", "status": "pending"},
        {"title": "Create reporting dashboard", "project": django_project, "priority": "high", "status": "completed"},
        {"title": "Add Claude AI business intelligence", "project": django_project, "priority": "medium", "status": "completed"},
        {"title": "Set up PostgreSQL production database", "project": django_project, "priority": "medium", "status": "pending"},
        {"title": "Configure Docker deployment", "project": django_project, "priority": "low", "status": "pending"},
        
        # General business tasks
        {"title": "Contact Harjeeve about land rental", "project": None, "priority": "urgent", "status": "pending"},
        {"title": "Prepare quarterly business review", "project": None, "priority": "high", "status": "pending"},
        {"title": "Update company registration to Shinobi Project", "project": None, "priority": "medium", "status": "pending"},
        {"title": "Research new market opportunities", "project": None, "priority": "low", "status": "pending"},
        {"title": "Organize digital asset backup", "project": None, "priority": "low", "status": "completed"},
    ]
    
    created_tasks = 0
    for task_data in tasks_data:
        Task.objects.create(
            title=task_data["title"],
            project=task_data["project"],
            assigned_to=jonin,
            priority=task_data["priority"],
            status=task_data["status"],
            description=f"Sample task: {task_data['title']}",
            due_date=timezone.now() + timedelta(days=randint(1, 30)),
            task_data={
                "estimated_hours": randint(1, 8),
                "sample_data": True
            }
        )
        created_tasks += 1
    
    print(f"✅ Created {created_tasks} tasks")
    
    # Create some financial entries
    print("💰 Creating financial entries...")
    financial_data = [
        {"amount": 250, "source": "Elias Student", "target": birdman, "type": "revenue", "desc": "Monthly guitar lessons"},
        {"amount": 150, "source": "Carol Leeming", "target": website_design, "type": "revenue", "desc": "Website deposit"},
        {"amount": 50, "source": haikutea, "target": "Cotswold Tea", "type": "expense", "desc": "Tea supplies"},
        {"amount": 500, "source": "Mike Investor", "target": haikutea, "type": "investment", "desc": "Initial investment"},
        {"amount": 75, "source": aaron_isaac, "target": "Book Sales", "type": "revenue", "desc": "Poetry book sales"},
    ]
    
    created_financials = 0
    for fin_data in financial_data:
        # Get or create entities for financial transactions
        if isinstance(fin_data["source"], str):
            source_entity, _ = Entity.objects.get_or_create(name=fin_data["source"])
        else:
            source_entity = fin_data["source"]
            
        if isinstance(fin_data["target"], str):
            target_entity, _ = Entity.objects.get_or_create(name=fin_data["target"])
        else:
            target_entity = fin_data["target"]
        
        FinancialEntry.objects.create(
            source_entity=source_entity,
            target_entity=target_entity,
            amount=fin_data["amount"],
            entry_type=fin_data["type"],
            description=fin_data["desc"],
            transaction_date=timezone.now().date() - timedelta(days=randint(1, 30)),
            financial_data={"sample_data": True}
        )
        created_financials += 1
    
    print(f"✅ Created {created_financials} financial entries")
    
    # Create some documents
    print("📄 Creating documents...")
    documents_data = [
        {"title": "HaikuTea Business Plan", "entity": haikutea, "type": "business_plan"},
        {"title": "Carol Leeming Website Specification", "entity": website_design, "type": "technical_spec"},
        {"title": "Birdman Tutoring Student Agreement", "entity": birdman, "type": "contract"},
        {"title": "Investment Proposal for HaikuTea", "entity": haikutea, "type": "proposal"},
        {"title": "Aaron Isaac Performance Contract", "entity": aaron_isaac, "type": "contract"},
    ]
    
    created_docs = 0
    for doc_data in documents_data:
        Document.objects.create(
            title=doc_data["title"],
            primary_entity=doc_data["entity"],
            document_type=doc_data["type"],
            content=f"Sample document content for {doc_data['title']}",
            document_data={
                "sample_data": True,
                "version": "1.0",
                "status": "active"
            }
        )
        created_docs += 1
    
    print(f"✅ Created {created_docs} documents")
    
    print("\n🎉 SAMPLE DATA CREATION COMPLETE!")
    print("=" * 50)
    print("📊 Current data summary:")
    print(f"- Time entries: {TimeEntry.objects.count()}")
    print(f"- Tasks: {Task.objects.count()}")
    print(f"- Financial entries: {FinancialEntry.objects.count()}")
    print(f"- Documents: {Document.objects.count()}")
    print(f"- Projects: {Project.objects.count()}")
    print(f"- Entities: {Entity.objects.count()}")
    print("\n✨ Your dashboard will now show rich visualizations!")
    print("🌐 Visit: http://localhost:8001/")

if __name__ == "__main__":
    create_sample_data()