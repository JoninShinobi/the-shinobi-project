from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

class EntityType(models.TextChoices):
    ORGANIZATION = 'organization', 'Organization'
    INDIVIDUAL = 'individual', 'Individual'
    EXTERNAL_ENTITY = 'external', 'External Entity'
    VENUE = 'venue', 'Venue'
    RESOURCE = 'resource', 'Resource'

class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    status = models.CharField(max_length=50, default='active')
    description = models.TextField(blank=True)
    
    # Flexible metadata using JSONB
    metadata = models.JSONField(default=dict, blank=True, help_text="Store contact info, capabilities, preferences, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Entities"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"
    
    @property
    def is_organization(self):
        return self.entity_type == EntityType.ORGANIZATION
    
    @property
    def is_individual(self):
        return self.entity_type == EntityType.INDIVIDUAL

class RelationshipType(models.TextChoices):
    MANAGES = 'manages', 'Manages'
    WORKS_FOR = 'works_for', 'Works For'
    SUPPLIES = 'supplies', 'Supplies'
    COLLABORATES = 'collaborates', 'Collaborates With'
    TEACHES = 'teaches', 'Teaches'
    LEARNS_FROM = 'learns_from', 'Learns From'
    INVESTS_IN = 'invests_in', 'Invests In'
    PROVIDES_VENUE = 'provides_venue', 'Provides Venue'
    USES_SERVICES = 'uses_services', 'Uses Services'
    SHARES_RESOURCES = 'shares_resources', 'Shares Resources'
    CLIENT_OF = 'client_of', 'Client Of'
    CONTRACTOR_FOR = 'contractor_for', 'Contractor For'

class EntityRelationship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    entity_a = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='relationships_as_a')
    entity_b = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='relationships_as_b')
    
    relationship_type = models.CharField(max_length=50, choices=RelationshipType.choices)
    strength = models.IntegerField(default=5, help_text="1-10 scale of relationship importance")
    is_bidirectional = models.BooleanField(default=True)
    
    # Flexible relationship data
    relationship_data = models.JSONField(default=dict, blank=True, help_text="Contract terms, shared projects, communication preferences, etc.")
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['entity_a', 'entity_b', 'relationship_type']
        verbose_name = "Entity Relationship"
    
    def __str__(self):
        return f"{self.entity_a.name} {self.get_relationship_type_display()} {self.entity_b.name}"

class ProjectStatus(models.TextChoices):
    PLANNING = 'planning', 'Planning'
    ACTIVE = 'active', 'Active'
    ON_HOLD = 'on_hold', 'On Hold'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # Project relationships
    primary_organization = models.ForeignKey(
        Entity, 
        on_delete=models.CASCADE,
        limit_choices_to={'entity_type': EntityType.ORGANIZATION},
        related_name='primary_projects'
    )
    related_entities = models.ManyToManyField(Entity, blank=True, related_name='involved_projects')
    
    # Project timeline
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNING)
    start_date = models.DateField(null=True, blank=True)
    target_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    
    # JSONB for project-specific data
    project_data = models.JSONField(default=dict, blank=True, help_text="Budget, milestones, resources, deliverables, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.primary_organization.name})"
    
    @property
    def is_active(self):
        return self.status == ProjectStatus.ACTIVE
    
    @property
    def is_overdue(self):
        if self.target_completion and self.status != ProjectStatus.COMPLETED:
            return timezone.now().date() > self.target_completion
        return False

class TaskStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    BLOCKED = 'blocked', 'Blocked'

class TaskPriority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Task relationships
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    assigned_to = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_tasks')
    related_entities = models.ManyToManyField(Entity, blank=True, related_name='related_tasks')
    
    # Task management
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    priority = models.CharField(max_length=10, choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # JSONB for task-specific data
    task_data = models.JSONField(default=dict, blank=True, help_text="Instructions, dependencies, resources, notes, etc.")
    
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.status})"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return timezone.now() > self.due_date
        return False

class TimeEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who, what, when
    person = models.ForeignKey(
        Entity, 
        on_delete=models.CASCADE,
        limit_choices_to={'entity_type': EntityType.INDIVIDUAL},
        related_name='person_time_entries'
    )
    organization = models.ForeignKey(
        Entity, 
        on_delete=models.CASCADE,
        limit_choices_to={'entity_type': EntityType.ORGANIZATION},
        null=True, 
        blank=True,
        related_name='organization_time_entries'
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='time_entries')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='time_entries')
    
    # Time details
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Entry metadata
    description = models.TextField(blank=True)
    entry_method = models.CharField(max_length=20, default='manual')  # 'whatsapp', 'web', 'api'
    
    # JSONB for flexible tracking data
    tracking_data = models.JSONField(default=dict, blank=True, help_text="Location, tools used, outcomes, WhatsApp data, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = "Time Entry"
        verbose_name_plural = "Time Entries"
    
    def save(self, *args, **kwargs):
        # Auto-calculate duration if both start and end times are set
        if self.start_time and self.end_time and not self.duration:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)
    
    def __str__(self):
        org_name = self.organization.name if self.organization else 'General'
        duration_str = str(self.duration) if self.duration else 'Ongoing'
        return f"{self.person.name} - {org_name} ({duration_str})"
    
    @property
    def is_active(self):
        return self.start_time and not self.end_time
    
    @property
    def duration_hours(self):
        if self.duration:
            return self.duration.total_seconds() / 3600
        return 0

class DocumentType(models.TextChoices):
    BUSINESS_PLAN = 'business_plan', 'Business Plan'
    CONTRACT = 'contract', 'Contract'
    INVOICE = 'invoice', 'Invoice'
    MEETING_NOTES = 'meeting_notes', 'Meeting Notes'
    TECHNICAL_SPEC = 'technical_spec', 'Technical Specification'
    CORRESPONDENCE = 'correspondence', 'Correspondence'
    REPORT = 'report', 'Report'
    PROPOSAL = 'proposal', 'Proposal'
    POLICY = 'policy', 'Policy'

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    
    # Document relationships
    primary_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='primary_documents')
    related_entities = models.ManyToManyField(Entity, blank=True, related_name='related_documents')
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    
    # Content
    content = models.TextField(blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    
    # JSONB for document metadata
    document_data = models.JSONField(default=dict, blank=True, help_text="File info, approval status, version info, tags, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} ({self.primary_entity.name})"

class FinancialEntryType(models.TextChoices):
    REVENUE = 'revenue', 'Revenue'
    EXPENSE = 'expense', 'Expense'
    INVESTMENT = 'investment', 'Investment'
    LOAN = 'loan', 'Loan'
    GRANT = 'grant', 'Grant'

class RevenueCategory(models.TextChoices):
    SERVICE_FEE = 'service_fee', 'Service Fee'
    PRODUCT_SALE = 'product_sale', 'Product Sale'
    SUBSCRIPTION = 'subscription', 'Subscription'
    LESSON_FEE = 'lesson_fee', 'Lesson Fee'
    CONSULTING = 'consulting', 'Consulting'
    LICENSE = 'license', 'License'

class FinancialEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Financial relationships
    source_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='outgoing_finances')
    target_entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='incoming_finances')
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='financial_entries')
    
    # Financial details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')
    entry_type = models.CharField(max_length=20, choices=FinancialEntryType.choices)
    category = models.CharField(max_length=50, choices=RevenueCategory.choices, blank=True)
    description = models.TextField()
    
    # Dates
    transaction_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    
    # JSONB for financial metadata
    financial_data = models.JSONField(default=dict, blank=True, help_text="Payment method, tax info, invoice details, recurring info, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Financial Entry"
        verbose_name_plural = "Financial Entries"
    
    def __str__(self):
        return f"£{self.amount} - {self.source_entity.name} → {self.target_entity.name}"
    
    @property
    def is_overdue(self):
        if self.due_date and not self.paid_date:
            return timezone.now().date() > self.due_date
        return False

# WhatsApp Session Management
class WhatsAppSession(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True, blank=True)
    active_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    active_organization = models.ForeignKey(
        Entity, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='active_whatsapp_sessions',
        limit_choices_to={'entity_type': EntityType.ORGANIZATION}
    )
    is_tracking_time = models.BooleanField(default=False)
    current_time_entry = models.ForeignKey(TimeEntry, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session data
    session_data = models.JSONField(default=dict, blank=True)
    
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"WhatsApp Session: {self.phone_number}"

# Claude AI Integration
class ClaudeInteraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Context
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Interaction details
    query = models.TextField()
    response = models.TextField()
    interaction_type = models.CharField(max_length=50, default='general')  # 'analysis', 'planning', 'reporting'
    
    # Metadata
    interaction_data = models.JSONField(default=dict, blank=True, help_text="API parameters, tokens used, context data, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Claude Query: {self.query[:50]}..."
