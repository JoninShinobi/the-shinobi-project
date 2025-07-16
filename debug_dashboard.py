#!/usr/bin/env python
"""
Debug dashboard issues
"""
import os
import sys
import django

# Set up Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shinobi_ops.settings')
django.setup()

from reporting.views import get_overview_dashboard_data
from core.models import Entity, TimeEntry, Task, Project
from django.urls import reverse

def debug_dashboard():
    print("🐛 DASHBOARD DEBUG INFORMATION")
    print("=" * 50)
    
    # Check data
    print("📊 Data Summary:")
    print(f"- Entities: {Entity.objects.count()}")
    print(f"- Time Entries: {TimeEntry.objects.count()}")
    print(f"- Tasks: {Task.objects.count()}")
    print(f"- Projects: {Project.objects.count()}")
    
    # Check recent time entries
    print("\n⏰ Recent Time Entries:")
    for entry in TimeEntry.objects.order_by('-created_at')[:5]:
        print(f"- {entry.person.name}: {entry.description[:50]}... ({entry.duration})")
    
    # Check dashboard data
    print("\n📈 Dashboard Data:")
    try:
        overview_data = get_overview_dashboard_data()
        print(f"- Overview data generated: ✅")
        print(f"- Total entities in overview: {overview_data['total_entities']}")
        print(f"- Total time entries in overview: {overview_data['total_time_entries']}")
        print(f"- Entity distribution data: {len(overview_data['entity_distribution'])}")
        print(f"- Time tracking trends: {len(overview_data['time_tracking_trends'])}")
        print(f"- Relationship network nodes: {len(overview_data['relationship_network']['nodes'])}")
    except Exception as e:
        print(f"- Dashboard data error: ❌ {e}")
    
    # Check URLs
    print("\n🔗 URL Configuration:")
    try:
        from django.urls import resolve, reverse
        url = resolve('/')
        print(f"- Root URL resolves to: {url.view_name}")
        print(f"- Dashboard URL: ✅")
    except Exception as e:
        print(f"- URL error: ❌ {e}")
    
    # Check template
    print("\n📄 Template Check:")
    template_path = "/Users/aarondudfield/Company_Operations/The Shinobi Project Operations/Company_Wide/Project_Management/shinobi_ops/reporting/templates/reporting/dashboard.html"
    if os.path.exists(template_path):
        print(f"- Template exists: ✅")
        with open(template_path, 'r') as f:
            content = f.read()
            print(f"- Template size: {len(content)} characters")
            print(f"- Contains charts: {'Chart.js' in content}")
            print(f"- Contains D3: {'d3js.org' in content}")
    else:
        print(f"- Template missing: ❌")
    
    # Check settings
    print("\n⚙️ Settings Check:")
    from django.conf import settings
    print(f"- DEBUG: {settings.DEBUG}")
    print(f"- ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"- INSTALLED_APPS includes reporting: {'reporting' in settings.INSTALLED_APPS}")
    
    print("\n🌐 Access Information:")
    print("- Dashboard URL: http://localhost:8001/")
    print("- Admin URL: http://localhost:8001/admin/")
    print("- Try opening in browser first")
    print("- Check browser console (F12) for JavaScript errors")
    print("- Look for any error messages on the page")

if __name__ == "__main__":
    debug_dashboard()