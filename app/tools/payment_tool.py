from sqlalchemy import create_engine, Column, Integer, String, Float, Date, text
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import date, timedelta
import random

# Database setup
engine = create_engine('sqlite:///payments.db')

class Base(DeclarativeBase):
    pass

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    tenant_name = Column(String(255), nullable=False)
    property_id = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False)

def create_tables():
    Base.metadata.create_all(engine)

def seed_data():
    """Seed the database with sample tenant payment records"""
    """Create sample tenant payment data"""
    with Session(engine) as session:
        # Check if data exists
        existing = session.execute(text("SELECT COUNT(*) FROM payments")).scalar()
        if existing > 0:
            return
        
        tenants = [
            ("Rajesh Kumar", "FLAT-1A"),
            ("Priya Sharma", "FLAT-2B"),
            ("Amit Singh", "FLAT-3C"),
        ]
        
        today = date.today()
        
        for tenant, prop in tenants:
            for i in range(3):  # 3 months of data
                due = today.replace(day=1) - timedelta(days=30*i)
                # Randomly mark some as overdue
                if i == 0 and random.random() > 0.5:
                    status = "pending"
                    paid_date = None
                else:
                    status = "paid"
                    paid_date = due + timedelta(days=random.randint(0, 5))
                
                session.add(Payment(
                    tenant_name=tenant,
                    property_id=prop,
                    amount=15000.0,
                    due_date=due,
                    paid_date=paid_date,
                    status=status
                ))
        
        session.commit()
        print("Sample data seeded")

def get_payment_status(tenant_name: str) -> str:
    """Get payment history for a tenant"""
    with Session(engine) as session:
        payments = session.query(Payment).filter(
            Payment.tenant_name.ilike(f"%{tenant_name}%")
        ).order_by(Payment.due_date.desc()).all()
        
        if not payments:
            return f"No payment records found for {tenant_name}"
        
        result = f"Payment history for {payments[0].tenant_name}:\n"
        for p in payments:
            result += f"- {p.due_date}: Rs.{p.amount:.0f} — {p.status.upper()}"
            if p.paid_date:
                result += f" (paid on {p.paid_date})"
            result += "\n"
        
        return result
    
def get_overdue_tenants() -> str:
    """Get all tenants with overdue or pending payments"""
    with Session(engine) as session:
        overdue = session.query(Payment).filter(
            Payment.status.in_(["pending", "overdue"])
        ).all()
        
        if not overdue:
            return "All tenants are up to date with payments"
        
        result = "Tenants with pending/overdue payments:\n"
        for p in overdue:
            days_late = (date.today() - p.due_date).days
            result += f"- {p.tenant_name} ({p.property_id}): Rs.{p.amount:.0f} due {p.due_date} — {days_late} days late\n"
        
        return result
    
# Initialize on import
create_tables()
seed_data()

