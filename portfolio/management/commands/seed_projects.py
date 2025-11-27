from django.core.management.base import BaseCommand
from portfolio.models import Project


class Command(BaseCommand):
    help = 'Seed the database with portfolio projects'

    def handle(self, *args, **options):
        projects = [
            {
                'name': 'Sound Box',
                'slug': 'sound-box',
                'category': 'application',
                'description': 'An innovative audio application designed to enhance the listening experience with curated soundscapes and audio tools.',
                'tech_stack': ['React', 'Audio API', 'Node.js'],
                'gradient_color': 'from-purple-600 to-indigo-700',
                'featured': True,
                'order': 1,
            },
            {
                'name': 'Hortus Cognitor',
                'slug': 'hortus-cognitor',
                'category': 'knowledge_platform',
                'description': 'A botanical knowledge system that helps gardeners and horticulturists identify, track, and cultivate plants with precision.',
                'tech_stack': ['Python', 'Machine Learning', 'Django'],
                'gradient_color': 'from-green-600 to-emerald-700',
                'featured': True,
                'order': 2,
            },
            {
                'name': 'Kerry Gallagher',
                'slug': 'kerry-gallagher',
                'category': 'personal_website',
                'description': 'A sophisticated personal website showcasing professional work and creative portfolio with elegant design.',
                'tech_stack': ['Next.js', 'Tailwind CSS', 'Vercel'],
                'gradient_color': 'from-amber-600 to-orange-700',
                'featured': False,
                'order': 3,
            },
            {
                'name': 'Community Harvest Whetstone',
                'slug': 'community-harvest-whetstone',
                'category': 'community_platform',
                'description': 'A local community initiative connecting neighbors through shared harvesting, food sharing, and sustainable agriculture practices.',
                'tech_stack': ['Django', 'PostgreSQL', 'Bootstrap'],
                'gradient_color': 'from-lime-600 to-green-700',
                'featured': True,
                'order': 4,
            },
            {
                'name': 'The Laurel',
                'slug': 'the-laurel',
                'category': 'business_platform',
                'description': 'A refined digital presence for a local business, featuring booking systems and customer engagement tools.',
                'tech_stack': ['React', 'Node.js', 'MongoDB'],
                'gradient_color': 'from-teal-600 to-cyan-700',
                'featured': False,
                'order': 5,
            },
            {
                'name': 'What Is Real',
                'slug': 'what-is-real',
                'category': 'creative_project',
                'description': 'An experimental digital experience exploring themes of perception, reality, and the boundaries of digital interaction.',
                'tech_stack': ['Three.js', 'WebGL', 'React'],
                'gradient_color': 'from-rose-600 to-pink-700',
                'featured': False,
                'order': 6,
            },
            {
                'name': 'HaikuTea',
                'slug': 'haiku-tea',
                'category': 'ecommerce',
                'description': 'An artisanal tea brand website combining traditional Japanese aesthetics with modern e-commerce functionality.',
                'tech_stack': ['Shopify', 'Liquid', 'JavaScript'],
                'gradient_color': 'from-red-600 to-rose-700',
                'featured': True,
                'order': 7,
            },
        ]

        for project_data in projects:
            project, created = Project.objects.update_or_create(
                slug=project_data['slug'],
                defaults=project_data
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{status}: {project.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded all projects'))
