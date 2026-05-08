from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Base schemas
class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: int
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: int
    
    class Config:
        from_attributes = True


class EquipmentTypeBase(BaseModel):
    name: str


class EquipmentTypeCreate(EquipmentTypeBase):
    pass


class EquipmentTypeRead(EquipmentTypeBase):
    id: int
    
    class Config:
        from_attributes = True


class StatusBase(BaseModel):
    name: str
    equipment_type_id: int


class StatusCreate(StatusBase):
    pass


class StatusRead(StatusBase):
    id: int
    equipment_type: Optional[EquipmentTypeRead] = None
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    full_name: str
    department_id: int
    role_id: int


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department_id: Optional[int] = None
    role_id: Optional[int] = None


class UserRead(UserBase):
    id: int
    department: Optional[DepartmentRead] = None
    role: Optional[RoleRead] = None
    
    class Config:
        from_attributes = True


class EquipmentBase(BaseModel):
    name: str
    barcode: str
    equipment_type_id: int
    status_id: int
    department_id: Optional[int] = None
    user_id: Optional[int] = None
    comment: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    created_by_id: Optional[int] = None


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    status_id: Optional[int] = None
    department_id: Optional[int] = None
    user_id: Optional[int] = None
    comment: Optional[str] = None


class EquipmentRead(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    equipment_type: Optional[EquipmentTypeRead] = None
    status: Optional[StatusRead] = None
    department: Optional[DepartmentRead] = None
    user: Optional[UserRead] = None
    
    class Config:
        from_attributes = True


class MovementHistoryBase(BaseModel):
    equipment_id: int
    status_id: int
    department_id: Optional[int] = None
    user_id: int
    comment: Optional[str] = None


class MovementHistoryCreate(MovementHistoryBase):
    pass


class MovementHistoryRead(MovementHistoryBase):
    id: int
    created_at: datetime
    equipment: Optional[EquipmentRead] = None
    status: Optional[StatusRead] = None
    department: Optional[DepartmentRead] = None
    user: Optional[UserRead] = None
    
    class Config:
        from_attributes = True


# Schemas for specific operations
class BarcodeScan(BaseModel):
    barcode: str


class MultipleBarcodeScan(BaseModel):
    barcodes: List[str]


class StatusChange(BaseModel):
    barcodes: List[str]
    status_id: int
    comment: Optional[str] = None
    target_user_id: Optional[int] = None  # For "Перемещение" status


class MovementHistoryFilter(BaseModel):
    equipment_id: Optional[int] = None
    user_id: Optional[int] = None
    department_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    equipment_name: Optional[str] = None
