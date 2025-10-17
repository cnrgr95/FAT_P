#!/usr/bin/env python3
"""
Database initialization script for Cost Calculation System
Run this script to create the database and initial data
"""

import os
import sys
from datetime import datetime
from app import app, db, User, Cost, TourProgram, SystemSetting

def create_database():
    """Create database tables"""
    print("Creating database tables...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully")
        
        # Create test user if not exists
        test_user = User.query.filter_by(username='admin').first()
        if not test_user:
            test_user = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                department='IT',
                position='System Administrator',
                is_active=True
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created (admin/admin123)")
        else:
            print("Test user already exists")
        
        # Create sample costs if none exist
        if Cost.query.count() == 0:
            sample_costs = [
                Cost(
                    name='Hotel Accommodation',
                    description='3 nights hotel stay in Istanbul',
                    amount=450.00,
                    category='Accommodation',
                    date=datetime.now().date(),
                    user_id=test_user.id
                ),
                Cost(
                    name='Flight Tickets',
                    description='Round trip flight tickets',
                    amount=800.00,
                    category='Travel',
                    date=datetime.now().date(),
                    user_id=test_user.id
                ),
                Cost(
                    name='Meals',
                    description='Daily meals and dining',
                    amount=200.00,
                    category='Food',
                    date=datetime.now().date(),
                    user_id=test_user.id
                )
            ]
            
            for cost in sample_costs:
                db.session.add(cost)
            
            db.session.commit()
            print("Sample cost data created")
        else:
            print("Cost data already exists")
        
        # Create sample tour programs if none exist
        if TourProgram.query.count() == 0:
            sample_tours = [
                TourProgram(
                    name='Istanbul City Tour',
                    description='3-day cultural tour of Istanbul',
                    start_date=datetime.now().date(),
                    end_date=datetime.now().date(),
                    destination='Istanbul, Turkey',
                    total_cost=1450.00,
                    user_id=test_user.id
                ),
                TourProgram(
                    name='Cappadocia Adventure',
                    description='2-day adventure tour in Cappadocia',
                    start_date=datetime.now().date(),
                    end_date=datetime.now().date(),
                    destination='Cappadocia, Turkey',
                    total_cost=750.00,
                    user_id=test_user.id
                )
            ]
            
            for tour in sample_tours:
                db.session.add(tour)
            
            db.session.commit()
            print("Sample tour program data created")
        else:
            print("Tour program data already exists")
        
        # Create system settings if none exist
        if SystemSetting.query.count() == 0:
            system_settings = [
                SystemSetting(
                    key='default_language',
                    value='en',
                    description='Default system language'
                ),
                SystemSetting(
                    key='currency',
                    value='USD',
                    description='Default currency for costs'
                ),
                SystemSetting(
                    key='date_format',
                    value='%Y-%m-%d',
                    description='Default date format'
                ),
                SystemSetting(
                    key='items_per_page',
                    value='10',
                    description='Number of items per page in listings'
                )
            ]
            
            for setting in system_settings:
                db.session.add(setting)
            
            db.session.commit()
            print("System settings created")
        else:
            print("System settings already exist")
        
        print("\nDatabase initialization completed successfully!")
        print("\nYou can now run the application with: python app.py")
        print("Login credentials: admin / admin123")

if __name__ == '__main__':
    try:
        create_database()
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
