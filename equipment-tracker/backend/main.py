from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import models
from init_db import init_db
from database import get_db

app = FastAPI(
    title="Equipment Tracker API",
    description="API для учета движения оборудования",
    version="1.0.0"
)


# Dependency
def get_database_session():
    db = get_db()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db = next(get_database_session())
    try:
        init_db(db)
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()


# Department endpoints
@app.get("/api/departments", response_model=List[dict])
def get_departments(db: Session = Depends(get_database_session)):
    departments = db.query(models.Department).all()
    return departments


# Role endpoints
@app.get("/api/roles", response_model=List[dict])
def get_roles(db: Session = Depends(get_database_session)):
    roles = db.query(models.Role).all()
    return roles


# Equipment Type endpoints
@app.get("/api/equipment-types", response_model=List[dict])
def get_equipment_types(db: Session = Depends(get_database_session)):
    equipment_types = db.query(models.EquipmentType).all()
    return equipment_types


# Status endpoints
@app.get("/api/statuses", response_model=List[dict])
def get_statuses(db: Session = Depends(get_database_session), equipment_type_id: Optional[int] = None):
    if equipment_type_id:
        statuses = db.query(models.Status).filter(
            models.Status.equipment_type_id == equipment_type_id
        ).all()
    else:
        statuses = db.query(models.Status).all()
    return statuses


# User endpoints
@app.get("/api/users", response_model=List[dict])
def get_users(db: Session = Depends(get_database_session)):
    users = db.query(models.User).all()
    return users


@app.post("/api/users")
def create_user(full_name: str, department_id: int, role_id: int, db: Session = Depends(get_database_session)):
    user = models.User(
        full_name=full_name,
        department_id=department_id,
        role_id=role_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Equipment endpoints
@app.get("/api/equipment", response_model=List[dict])
def get_equipment(
    db: Session = Depends(get_database_session),
    equipment_type_id: Optional[int] = None,
    status_id: Optional[int] = None,
    department_id: Optional[int] = None,
    barcode: Optional[str] = None
):
    query = db.query(models.Equipment)
    
    if equipment_type_id:
        query = query.filter(models.Equipment.equipment_type_id == equipment_type_id)
    if status_id:
        query = query.filter(models.Equipment.status_id == status_id)
    if department_id:
        query = query.filter(models.Equipment.department_id == department_id)
    if barcode:
        query = query.filter(models.Equipment.barcode == barcode)
    
    equipment_list = query.all()
    return equipment_list


@app.get("/api/equipment/{barcode}")
def get_equipment_by_barcode(barcode: str, db: Session = Depends(get_database_session)):
    equipment = db.query(models.Equipment).filter(models.Equipment.barcode == barcode).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@app.post("/api/equipment")
def create_equipment(
    name: str,
    barcode: str,
    equipment_type_id: int,
    status_id: int,
    department_id: Optional[int] = None,
    user_id: Optional[int] = None,
    comment: Optional[str] = None,
    created_by_id: Optional[int] = 1,
    db: Session = Depends(get_database_session)
):
    # Check if barcode already exists
    existing = db.query(models.Equipment).filter(models.Equipment.barcode == barcode).first()
    if existing:
        raise HTTPException(status_code=400, detail="Equipment with this barcode already exists")
    
    equipment = models.Equipment(
        name=name,
        barcode=barcode,
        equipment_type_id=equipment_type_id,
        status_id=status_id,
        department_id=department_id,
        user_id=user_id,
        comment=comment,
        created_by_id=created_by_id
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    
    # Create initial movement history entry
    movement = models.MovementHistory(
        equipment_id=equipment.id,
        status_id=status_id,
        department_id=department_id,
        user_id=created_by_id,
        comment="Начальная запись"
    )
    db.add(movement)
    db.commit()
    
    return equipment


@app.put("/api/equipment/{equipment_id}")
def update_equipment(
    equipment_id: int,
    name: Optional[str] = None,
    status_id: Optional[int] = None,
    department_id: Optional[int] = None,
    user_id: Optional[int] = None,
    comment: Optional[str] = None,
    db: Session = Depends(get_database_session)
):
    equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    if name is not None:
        equipment.name = name
    if status_id is not None:
        equipment.status_id = status_id
    if department_id is not None:
        equipment.department_id = department_id
    if user_id is not None:
        equipment.user_id = user_id
    if comment is not None:
        equipment.comment = comment
    
    db.commit()
    db.refresh(equipment)
    return equipment


# Movement History endpoints
@app.get("/api/movement-history", response_model=List[dict])
def get_movement_history(
    db: Session = Depends(get_database_session),
    equipment_id: Optional[int] = None,
    user_id: Optional[int] = None,
    department_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    equipment_name: Optional[str] = None
):
    query = db.query(models.MovementHistory)
    
    if equipment_id:
        query = query.filter(models.MovementHistory.equipment_id == equipment_id)
    if user_id:
        query = query.filter(models.MovementHistory.user_id == user_id)
    if department_id:
        query = query.filter(models.MovementHistory.department_id == department_id)
    if start_date:
        query = query.filter(models.MovementHistory.created_at >= start_date)
    if end_date:
        query = query.filter(models.MovementHistory.created_at <= end_date)
    if equipment_name:
        equipment_ids = db.query(models.Equipment.id).filter(
            models.Equipment.name.contains(equipment_name)
        ).all()
        equipment_ids = [eq[0] for eq in equipment_ids]
        query = query.filter(models.MovementHistory.equipment_id.in_(equipment_ids))
    
    history = query.order_by(models.MovementHistory.created_at.desc()).all()
    return history


@app.post("/api/movement/change-status")
def change_status(
    barcodes: List[str],
    status_id: int,
    user_id: int,
    comment: Optional[str] = None,
    target_user_id: Optional[int] = None,
    db: Session = Depends(get_database_session)
):
    """Change status for multiple equipment items by barcode"""
    results = []
    
    for barcode in barcodes:
        equipment = db.query(models.Equipment).filter(models.Equipment.barcode == barcode).first()
        if not equipment:
            results.append({
                "barcode": barcode,
                "success": False,
                "error": "Equipment not found"
            })
            continue
        
        # Update equipment status
        equipment.status_id = status_id
        if target_user_id:
            equipment.user_id = target_user_id
        if comment:
            equipment.comment = comment
        
        # Create movement history entry
        movement = models.MovementHistory(
            equipment_id=equipment.id,
            status_id=status_id,
            department_id=equipment.department_id,
            user_id=user_id,
            comment=comment
        )
        db.add(movement)
        
        results.append({
            "barcode": barcode,
            "success": True,
            "equipment_id": equipment.id,
            "equipment_name": equipment.name
        })
    
    db.commit()
    return {"results": results}


# Get equipment not in "В работе" status
@app.get("/api/equipment/not-active")
def get_not_active_equipment(
    db: Session = Depends(get_database_session),
    equipment_type_id: Optional[int] = None
):
    """Get equipment that is not in active status (not 'МОЛ' or 'В работе')"""
    # Find statuses that indicate active work
    active_status_names = ["МОЛ"]
    active_statuses = db.query(models.Status.id).filter(
        models.Status.name.in_(active_status_names)
    ).all()
    active_status_ids = [s[0] for s in active_statuses]
    
    query = db.query(models.Equipment).filter(
        ~models.Equipment.status_id.in_(active_status_ids)
    )
    
    if equipment_type_id:
        query = query.filter(models.Equipment.equipment_type_id == equipment_type_id)
    
    equipment = query.all()
    return equipment


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
