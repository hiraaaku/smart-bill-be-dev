# create_user.py
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

def create_user(name: str):
    db: Session = SessionLocal()
    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    print("User created:")
    print("ID:", user.id)
    print("Name:", user.name)

if __name__ == "__main__":
    create_user("Hira")
