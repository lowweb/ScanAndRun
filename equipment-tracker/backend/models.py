from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://equipment_user:equipment_pass@localhost:5432/equipment_tracker")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    users = relationship("User", back_populates="department")
    equipment = relationship("Equipment", back_populates="department")
    movement_history = relationship("MovementHistory", back_populates="department")


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    users = relationship("User", back_populates="role")


class EquipmentType(Base):
    __tablename__ = "equipment_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    statuses = relationship("Status", back_populates="equipment_type")
    equipment = relationship("Equipment", back_populates="equipment_type")


class Status(Base):
    __tablename__ = "statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    equipment_type_id = Column(Integer, ForeignKey("equipment_types.id"), nullable=False)
    
    equipment_type = relationship("EquipmentType", back_populates="statuses")
    equipment = relationship("Equipment", back_populates="status")
    movement_history = relationship("MovementHistory", back_populates="status")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    login = Column(String(50), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    
    equipment = relationship("Equipment", back_populates="user", foreign_keys="Equipment.user_id")
    created_equipment = relationship("Equipment", back_populates="created_by", foreign_keys="Equipment.created_by_id")
    movement_history = relationship("MovementHistory", back_populates="user")


class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    barcode = Column(String(100), unique=True, nullable=False, index=True)
    equipment_type_id = Column(Integer, ForeignKey("equipment_types.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    comment = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    equipment_type = relationship("EquipmentType", back_populates="equipment")
    status = relationship("Status", back_populates="equipment")
    department = relationship("Department", back_populates="equipment")
    user = relationship("User", back_populates="equipment", foreign_keys=[user_id])
    created_by = relationship("User", back_populates="created_equipment", foreign_keys=[created_by_id])
    
    movement_history = relationship("MovementHistory", back_populates="equipment", order_by="MovementHistory.created_at.desc()")


class MovementHistory(Base):
    __tablename__ = "movement_history"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    equipment = relationship("Equipment", back_populates="movement_history")
    status = relationship("Status", back_populates="movement_history")
    department = relationship("Department", back_populates="movement_history")
    user = relationship("User", back_populates="movement_history")
