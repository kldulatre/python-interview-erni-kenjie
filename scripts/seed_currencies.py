"""
Database Seeder for Supported Currencies.
Run this script to initialize the `currencies` table with defaults.
"""
import sys
import os

# Ensure the app module can be found when running from the command line
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.models.currency_model import CurrencyModel

def seed():
    # Attempt to create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        defaults = [
            ("PHP", "Philippine Peso"),
            ("USD", "US Dollar"),
            ("EUR", "Euro"),
            ("SGD", "Singapore Dollar"),
        ]
        
        for code, name in defaults:
            existing = db.query(CurrencyModel).filter(CurrencyModel.code == code).first()
            if not existing:
                print(f"Seeding: {code} - {name}")
                db.add(CurrencyModel(code=code, name=name))
            else:
                print(f"Already exists: {code}")
        
        db.commit()
        print("Completed currency seeding!")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
