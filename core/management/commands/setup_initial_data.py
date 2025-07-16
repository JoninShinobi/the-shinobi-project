from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Entity, EntityType, EntityRelationship, RelationshipType, Project, ProjectStatus

class Command(BaseCommand):
    help = 'Set up initial Shinobi Project entities and relationships'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up initial data for The Shinobi Project...'))
        
        # Create core entities
        entities = {}
        
        # Organizations
        self.stdout.write('Creating organizations...')
        
        entities['shinobi_project'] = Entity.objects.get_or_create(
            name="The Shinobi Project",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Parent company managing multiple business ventures',
                'metadata': {
                    'business_type': 'holding_company',
                    'legal_structure': 'ltd_company',
                    'services': ['business_management', 'strategic_planning', 'operations'],
                    'status': 'active'
                }
            }
        )[0]
        
        entities['aaron_isaac'] = Entity.objects.get_or_create(
            name="Aaron Isaac",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Creative arts brand - poetry, music, published works',
                'metadata': {
                    'business_type': 'creative_arts',
                    'services': ['poetry', 'music', 'published_works'],
                    'website': 'aaronisaac.com',
                    'products': ['poetry_books', 'music_performances']
                }
            }
        )[0]
        
        entities['birdman_tutoring'] = Entity.objects.get_or_create(
            name="Birdman Tutoring",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Guitar lessons and music education',
                'metadata': {
                    'business_type': 'education',
                    'services': ['guitar_lessons', 'music_education'],
                    'technologies': ['django', 'lms'],
                    'target_audience': 'beginner_guitarists'
                }
            }
        )[0]
        
        entities['haikutea'] = Entity.objects.get_or_create(
            name="HaikuTea",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Poetry tea company - poems on tea packets',
                'metadata': {
                    'business_type': 'product',
                    'products': ['poetry_tea_packets'],
                    'website': 'haiku.kondoproperty.co.uk',
                    'target_market': 'tea_lovers_poetry_enthusiasts'
                }
            }
        )[0]
        
        entities['website_design'] = Entity.objects.get_or_create(
            name="Website Design Services",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Django-based web development services',
                'metadata': {
                    'business_type': 'technology_services',
                    'services': ['django_development', 'web_design', 'cms_development'],
                    'technologies': ['django', 'postgresql', 'docker'],
                    'target_market': 'small_businesses'
                }
            }
        )[0]
        
        entities['book_publishing'] = Entity.objects.get_or_create(
            name="Book Publishing Platform",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Poetry processing and layout automation',
                'metadata': {
                    'business_type': 'publishing',
                    'services': ['poetry_processing', 'layout_automation', 'book_publishing'],
                    'technologies': ['django', 'automation_tools'],
                    'target_market': 'poets_authors'
                }
            }
        )[0]
        
        entities['the_laurel'] = Entity.objects.get_or_create(
            name="The Laurel",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Community Supported Agriculture (CSA) project',
                'metadata': {
                    'business_type': 'agriculture',
                    'services': ['csa', 'organic_farming', 'community_supported_agriculture'],
                    'location': 'harjeeve_land',
                    'deadline': 'august_2025'
                }
            }
        )[0]
        
        entities['soundbox'] = Entity.objects.get_or_create(
            name="SoundBox",
            entity_type=EntityType.ORGANIZATION,
            defaults={
                'description': 'Events organization and music culture advocacy',
                'metadata': {
                    'business_type': 'events_advocacy',
                    'services': ['event_coordination', 'music_culture_advocacy', 'community_organizing'],
                    'technologies': ['django', 'event_management'],
                    'target_market': 'local_music_community'
                }
            }
        )[0]
        
        # Individuals
        self.stdout.write('Creating individuals...')
        
        entities['jonin'] = Entity.objects.get_or_create(
            name="Jonin (Aaron Dudfield)",
            entity_type=EntityType.INDIVIDUAL,
            defaults={
                'description': 'Employee and project manager',
                'metadata': {
                    'role': 'employee',
                    'skills': ['django', 'guitar', 'poetry', 'web_development', 'project_management'],
                    'responsibilities': ['technical_implementation', 'business_operations', 'time_tracking'],
                    'contact': {'whatsapp': '+44...'}  # Add actual phone for WhatsApp
                }
            }
        )[0]
        
        entities['elias'] = Entity.objects.get_or_create(
            name="Elias",
            entity_type=EntityType.INDIVIDUAL,
            defaults={
                'description': 'Guitar student at Birdman Tutoring',
                'metadata': {
                    'role': 'student',
                    'lesson_day': 'sunday',
                    'skill_level': 'beginner',
                    'payment_schedule': 'weekly',
                    'contact': {'method': 'whatsapp'}
                }
            }
        )[0]
        
        entities['carol_leeming'] = Entity.objects.get_or_create(
            name="Carol Leeming",
            entity_type=EntityType.INDIVIDUAL,
            defaults={
                'description': 'Website design client (MBE poet)',
                'metadata': {
                    'role': 'client',
                    'project_type': 'website_development',
                    'status': 'active_client',
                    'credentials': 'mbe_poet'
                }
            }
        )[0]
        
        entities['mike_investor'] = Entity.objects.get_or_create(
            name="Mike Investor",
            entity_type=EntityType.INDIVIDUAL,
            defaults={
                'description': 'Potential HaikuTea investor',
                'metadata': {
                    'role': 'potential_investor',
                    'interest': 'haikutea',
                    'status': 'prospect',
                    'contact_method': 'email'
                }
            }
        )[0]
        
        # External entities
        self.stdout.write('Creating external entities...')
        
        entities['linklings_cic'] = Entity.objects.get_or_create(
            name="Linklings Poets CIC",
            entity_type=EntityType.EXTERNAL_ENTITY,
            defaults={
                'description': 'Poetry collective organization',
                'metadata': {
                    'organization_type': 'cic',
                    'relationship': 'member_organization',
                    'services': ['poetry_collective', 'community_organizing'],
                    'status': 'active_collaboration'
                }
            }
        )[0]
        
        entities['cotswold_tea'] = Entity.objects.get_or_create(
            name="Cotswold Tea",
            entity_type=EntityType.EXTERNAL_ENTITY,
            defaults={
                'description': 'HaikuTea supplier',
                'metadata': {
                    'organization_type': 'supplier',
                    'products': ['tea_supplies'],
                    'relationship': 'supplier',
                    'status': 'active_supplier'
                }
            }
        )[0]
        
        entities['harjeeve_landowner'] = Entity.objects.get_or_create(
            name="Harjeeve Landowner",
            entity_type=EntityType.EXTERNAL_ENTITY,
            defaults={
                'description': 'Land rental partner for The Laurel',
                'metadata': {
                    'organization_type': 'landowner',
                    'services': ['land_rental'],
                    'relationship': 'land_partnership',
                    'deadline': 'august_2025'
                }
            }
        )[0]
        
        # Create relationships
        self.stdout.write('Creating relationships...')
        
        relationships = [
            # Management relationships
            (entities['jonin'], RelationshipType.MANAGES, entities['shinobi_project']),
            (entities['shinobi_project'], RelationshipType.MANAGES, entities['aaron_isaac']),
            (entities['shinobi_project'], RelationshipType.MANAGES, entities['birdman_tutoring']),
            (entities['shinobi_project'], RelationshipType.MANAGES, entities['haikutea']),
            (entities['shinobi_project'], RelationshipType.MANAGES, entities['website_design']),
            (entities['shinobi_project'], RelationshipType.MANAGES, entities['book_publishing']),
            (entities['shinobi_project'], RelationshipType.MANAGES, entities['the_laurel']),
            (entities['shinobi_project'], RelationshipType.MANAGES, entities['soundbox']),
            
            # Teaching relationships
            (entities['jonin'], RelationshipType.TEACHES, entities['elias']),
            (entities['elias'], RelationshipType.LEARNS_FROM, entities['birdman_tutoring']),
            
            # Client relationships
            (entities['carol_leeming'], RelationshipType.CLIENT_OF, entities['website_design']),
            (entities['website_design'], RelationshipType.CONTRACTOR_FOR, entities['carol_leeming']),
            
            # Investment relationships
            (entities['mike_investor'], RelationshipType.INVESTS_IN, entities['haikutea']),
            
            # Supplier relationships
            (entities['cotswold_tea'], RelationshipType.SUPPLIES, entities['haikutea']),
            
            # Collaboration relationships
            (entities['aaron_isaac'], RelationshipType.COLLABORATES, entities['linklings_cic']),
            (entities['the_laurel'], RelationshipType.USES_SERVICES, entities['harjeeve_landowner']),
            
            # Cross-venture support
            (entities['website_design'], RelationshipType.SUPPLIES, entities['aaron_isaac']),
            (entities['website_design'], RelationshipType.SUPPLIES, entities['birdman_tutoring']),
            (entities['website_design'], RelationshipType.SUPPLIES, entities['haikutea']),
            (entities['website_design'], RelationshipType.SUPPLIES, entities['soundbox']),
        ]
        
        for entity_a, rel_type, entity_b in relationships:
            relationship, created = EntityRelationship.objects.get_or_create(
                entity_a=entity_a,
                entity_b=entity_b,
                relationship_type=rel_type,
                defaults={
                    'strength': 8,
                    'start_date': timezone.now().date(),
                    'relationship_data': {
                        'created_by': 'initial_setup',
                        'status': 'active'
                    }
                }
            )
            if created:
                self.stdout.write(f'  Created: {relationship}')
        
        # Create initial projects
        self.stdout.write('Creating initial projects...')
        
        projects = [
            {
                'name': 'Django Business Management System',
                'organization': entities['shinobi_project'],
                'description': 'Complete business management system with PostgreSQL + JSONB',
                'status': ProjectStatus.ACTIVE,
                'project_data': {
                    'technologies': ['django', 'postgresql', 'jsonb', 'claude_api'],
                    'milestones': [
                        {'name': 'Database Schema', 'status': 'completed'},
                        {'name': 'Django Models', 'status': 'in_progress'},
                        {'name': 'Admin Interface', 'status': 'pending'},
                        {'name': 'WhatsApp Integration', 'status': 'pending'}
                    ]
                }
            },
            {
                'name': 'HaikuTea Supply Chain Resolution',
                'organization': entities['haikutea'],
                'description': 'Resolve tea supply chain issues and packaging problems',
                'status': ProjectStatus.ACTIVE,
                'project_data': {
                    'priority': 'high',
                    'issues': ['packaging_problems', 'supplier_coordination'],
                    'contacts': ['cotswold_tea', 'mike_investor']
                }
            },
            {
                'name': 'Carol Leeming Website',
                'organization': entities['website_design'],
                'description': 'Website development for MBE poet Carol Leeming',
                'status': ProjectStatus.ACTIVE,
                'project_data': {
                    'client': 'carol_leeming',
                    'technologies': ['django', 'cms'],
                    'requirements': ['poetry_showcase', 'cms_functionality']
                }
            },
            {
                'name': 'The Laurel Land Acquisition',
                'organization': entities['the_laurel'],
                'description': 'Secure land rental agreement with Harjeeve before August deadline',
                'status': ProjectStatus.ACTIVE,
                'project_data': {
                    'deadline': 'august_2025',
                    'priority': 'urgent',
                    'requirements': ['land_rental_agreement', 'csa_setup']
                }
            }
        ]
        
        for project_data in projects:
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                primary_organization=project_data['organization'],
                defaults={
                    'description': project_data['description'],
                    'status': project_data['status'],
                    'project_data': project_data['project_data'],
                    'start_date': timezone.now().date()
                }
            )
            if created:
                self.stdout.write(f'  Created project: {project.name}')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup complete!'))
        self.stdout.write(f'Created {len(entities)} entities and {len(relationships)} relationships')
        self.stdout.write(f'Created {len(projects)} initial projects')
        
        self.stdout.write('\n' + self.style.SUCCESS('The Shinobi Project operational database is ready!'))
        self.stdout.write('You can now:')
        self.stdout.write('1. Access the admin interface at http://localhost:8000/admin')
        self.stdout.write('2. Create time entries via WhatsApp integration')
        self.stdout.write('3. Track cross-venture relationships and projects')
        self.stdout.write('4. Generate business intelligence reports')