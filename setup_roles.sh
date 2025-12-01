#!/bin/bash

# Shinobi C2 - Role Setup Script
# Executes SQL to create roles and policies in Directus

set -e

echo "🥷 Shinobi C2 - Setting up roles and policies..."
echo ""

# Check if Docker container is running
if ! docker ps | grep -q shinobi_vault; then
    echo "❌ Error: shinobi_vault container is not running"
    echo "   Start it with: docker-compose up -d"
    exit 1
fi

# Copy SQL file to container
echo "📋 Copying SQL file to container..."
docker cp setup_roles.sql shinobi_vault:/tmp/setup_roles.sql

# Execute SQL
echo "⚙️  Executing SQL commands..."
docker exec shinobi_vault psql -U shinobi -d shinobi_db -f /tmp/setup_roles.sql

# Clean up
echo "🧹 Cleaning up..."
docker exec shinobi_vault rm /tmp/setup_roles.sql

echo ""
echo "✅ Roles and policies created successfully!"
echo ""
echo "📊 Current roles:"
docker exec shinobi_vault psql -U shinobi -d shinobi_db -c "SELECT name, description FROM directus_roles ORDER BY name;"

echo ""
echo "🎯 Next steps:"
echo "1. Log into Directus at http://localhost:8055"
echo "2. Navigate to Settings > Access Control > Policies"
echo "3. Configure collection permissions for each policy"
echo "4. See PERMISSIONS_GUIDE.md for detailed instructions"
echo ""
