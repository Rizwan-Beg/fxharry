#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables and optionally seeds initial data.
"""

from sqlalchemy import create_engine, inspect
from ai_core.core.config import settings
from ai_core.database.database import Base, engine
from ai_core.database.models import (
    Strategy,
    Trade,
    BacktestResult,
    MarketData,
    AISignal,
    AccountSnapshot
)

def init_database():
    """Initialize the database by creating all tables."""
    print(f"🗄️  Initializing database...")
    print(f"📍 Database URL: {settings.database_url}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n✅ Database initialized successfully!")
    print(f"📊 Created {len(tables)} tables:")
    for table in tables:
        print(f"   - {table}")
    
    return True

def seed_test_data():
    """Optional: Seed initial test data."""
    from ai_core.database.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Check if apex strategy already exists
        apex = db.query(Strategy).filter_by(name="apex").first()
        if not apex:
            apex = Strategy(
                name="apex",
                description="Multi-timeframe trend-following strategy",
                strategy_type="python",
                file_path="ai_core/strategy_engine/strategies/apex_strategy.py",
                is_active=True,
                parameters={}
            )
            db.add(apex)
        
        # Check if riztest strategy already exists
        riztest = db.query(Strategy).filter_by(name="riztest").first()
        if not riztest:
            riztest = Strategy(
                name="riztest",
                description="Test strategy for end-to-end verification",
                strategy_type="python",
                file_path="ai_core/strategy_engine/strategies/riztest_strategy.py",
                is_active=True,
                parameters={"max_signals": 1}
            )
            db.add(riztest)
        
        db.commit()
        print(f"\n✅ Test data seeded successfully!")
        print(f"   - apex strategy: {apex.id if apex.id else 'created'}")
        print(f"   - riztest strategy: {riztest.id if riztest.id else 'created'}")
        
    except Exception as e:
        print(f"\n❌ Error seeding test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 FXHarry Trading Platform - Database Initialization")
    print("=" * 80)
    
    try:
        init_database()
        seed_test_data()
        print("\n" + "=" * 80)
        print("✅ Database setup complete!")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
