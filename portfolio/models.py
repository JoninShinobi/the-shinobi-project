from django.db import models


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('application', 'Application'),
        ('knowledge_platform', 'Knowledge Platform'),
        ('personal_website', 'Personal Website'),
        ('community_platform', 'Community Platform'),
        ('business_platform', 'Business Platform'),
        ('creative_project', 'Creative Project'),
        ('ecommerce', 'E-Commerce'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    tech_stack = models.JSONField(default=list)
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    gradient_color = models.CharField(max_length=100, default='from-red-600 to-rose-700')
    live_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class ContactSubmission(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    business_name = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"
