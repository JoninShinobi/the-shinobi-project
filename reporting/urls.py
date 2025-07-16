from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/entity/<uuid:entity_id>/', views.get_entity_data_json, name='entity_data'),
    path('api/ai-insights/<uuid:entity_id>/', views.get_ai_insights_json, name='ai_insights'),
    path('api/ai-insights/overview/', views.get_ai_insights_json, {'entity_id': None}, name='ai_insights_overview'),
    path('api/charts/', views.get_charts_data_json, name='charts_data'),
]