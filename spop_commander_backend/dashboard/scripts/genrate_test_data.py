# scripts/generate_test_data.py

import os
import django
import sys

sys.path.append('path_to_your_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spop_commander_backend.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


def clean_database():
    """Clean existing data from the database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 'TRUNCATE TABLE ' || table_name || ' CASCADE;'
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE';
            """)
            truncate_commands = cursor.fetchall()
            for command in truncate_commands:
                cursor.execute(command[0])
    except OperationalError as e:
        print(f"Error cleaning database: {e}")
        return False
    return True


def main():
    print("Starting test data generation...")

    # Clean existing data
    if clean_database():
        print("Database cleaned successfully")
    else:
        print("Error cleaning database")
        return

    # Generate new data
    try:
        call_command('generate_mock_data')
        print("Mock data generated successfully")
    except Exception as e:
        print(f"Error generating mock data: {e}")
        return

    print("Test data generation completed")


if __name__ == '__main__':
    main()