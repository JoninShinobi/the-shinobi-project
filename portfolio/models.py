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


class IncomingIntel(models.Model):
    """Tracks incoming leads and inquiries - The C2 Intelligence Feed"""
    INTEL_TYPE_CHOICES = [
        ('lead', 'Lead'),
        ('inquiry', 'Inquiry'),
        ('referral', 'Referral'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted'),
        ('archived', 'Archived'),
    ]

    source = models.CharField(max_length=100)  # website, referral, cold
    contact_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    business_name = models.CharField(max_length=200, blank=True)
    intel_type = models.CharField(max_length=50, choices=INTEL_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Incoming Intel"

    def __str__(self):
        return f"[{self.status}] {self.contact_name} - {self.intel_type}"


class BusinessMetrics(models.Model):
    """Tracks key business metrics over time - The C2 Dashboard Data"""
    date = models.DateField(unique=True)
    website_visits = models.IntegerField(default=0)
    leads_generated = models.IntegerField(default=0)
    proposals_sent = models.IntegerField(default=0)
    deals_closed = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Business Metrics"

    def __str__(self):
        return f"{self.date} - {self.leads_generated} leads, ${self.revenue}"
