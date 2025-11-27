from rest_framework import serializers
from .models import Project, ContactSubmission


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'slug', 'category', 'description',
            'tech_stack', 'image', 'gradient_color', 'live_url',
            'github_url', 'featured', 'created_at'
        ]


class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ['id', 'name', 'email', 'business_name', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
