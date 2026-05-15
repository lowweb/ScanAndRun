from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import (
    Department, Role, EquipmentType, Status, 
    User, Equipment, MovementHistory
)
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)


def init_db(db: Session):
    """Initialize database with test data"""
    
    # Create Departments
    departments_data = ["ИТ отдел", "Бухгалтерия", "Отдел продаж"]
    departments = {}
    for dept_name in departments_data:
        dept = db.query(Department).filter(Department.name == dept_name).first()
        if not dept:
            dept = Department(name=dept_name)
            db.add(dept)
        departments[dept_name] = dept
    
    db.commit()
    # Refresh to get IDs
    for dept_name in departments_data:
        departments[dept_name] = db.query(Department).filter(Department.name == dept_name).first()
    
    # Create Roles
    roles_data = ["admin", "user"]
    roles = {}
    for role_name in roles_data:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
    
    db.commit()
    for role_name in roles_data:
        roles[role_name] = db.query(Role).filter(Role.name == role_name).first()
    
    # Create Equipment Types
    equipment_types_data = ["Картридж", "Комп. и орг. техника"]
    equipment_types = {}
    for type_name in equipment_types_data:
        eq_type = db.query(EquipmentType).filter(EquipmentType.name == type_name).first()
        if not eq_type:
            eq_type = EquipmentType(name=type_name)
            db.add(eq_type)
    
    db.commit()
    for type_name in equipment_types_data:
        equipment_types[type_name] = db.query(EquipmentType).filter(EquipmentType.name == type_name).first()
    
    # Create Statuses for Cartridges
    cartridge_statuses = ["МОЛ", "Заправка", "Склад - на заправку", "Склад - выдача"]
    # Create Statuses for Computer Equipment
    computer_statuses = ["Склад", "Склад утилизация", "В ремонте", "ИТ отдел", "МОЛ", "Перемещение"]
    
    statuses = {}
    for status_name in cartridge_statuses:
        status = db.query(Status).filter(
            Status.name == status_name,
            Status.equipment_type_id == equipment_types["Картридж"].id
        ).first()
        if not status:
            status = Status(
                name=status_name,
                equipment_type_id=equipment_types["Картридж"].id
            )
            db.add(status)
    
    db.commit()
    for status_name in cartridge_statuses:
        statuses[f"cartridge_{status_name}"] = db.query(Status).filter(
            Status.name == status_name,
            Status.equipment_type_id == equipment_types["Картридж"].id
        ).first()
    
    for status_name in computer_statuses:
        status = db.query(Status).filter(
            Status.name == status_name,
            Status.equipment_type_id == equipment_types["Комп. и орг. техника"].id
        ).first()
        if not status:
            status = Status(
                name=status_name,
                equipment_type_id=equipment_types["Комп. и орг. техника"].id
            )
            db.add(status)
    
    db.commit()
    for status_name in computer_statuses:
        statuses[f"computer_{status_name}"] = db.query(Status).filter(
            Status.name == status_name,
            Status.equipment_type_id == equipment_types["Комп. и орг. техника"].id
        ).first()
    
    # Create Users
    users_data = [
        {"full_name": "Администратор Системы", "login": "admin", "department": "ИТ отдел", "role": "admin"},
        {"full_name": "Иван Иванов", "login": "ivanov", "department": "ИТ отдел", "role": "user"},
        {"full_name": "Петр Петров", "login": "petrov", "department": "Бухгалтерия", "role": "user"},
        {"full_name": "Мария Сидорова", "login": "sidorova", "department": "Отдел продаж", "role": "user"},
    ]
    
    users = {}
    for user_data in users_data:
        user = db.query(User).filter(User.login == user_data["login"]).first()
        if not user:
            user = User(
                full_name=user_data["full_name"],
                login=user_data["login"],
                password_hash=get_password_hash("123"),  # Default password for all test users
                department_id=departments[user_data["department"]].id,
                role_id=roles[user_data["role"]].id
            )
            db.add(user)
    
    db.commit()
    for user_data in users_data:
        users[user_data["full_name"]] = db.query(User).filter(User.login == user_data["login"]).first()
    
    # Create Test Equipment
    test_equipment = [
        # Cartridges
        {
            "name": "Картридж HP LaserJet 1010",
            "barcode": "CARTRIDGE001",
            "type": "Картридж",
            "status": "МОЛ",
            "department": "Бухгалтерия",
            "comment": "Установлен в принтер HP LaserJet 1010"
        },
        {
            "name": "Картридж Canon LBP3000",
            "barcode": "CARTRIDGE002",
            "type": "Картридж",
            "status": "Заправка",
            "department": None,
            "comment": "Требует заправки"
        },
        {
            "name": "Картридж Samsung ML-1640",
            "barcode": "CARTRIDGE003",
            "type": "Картридж",
            "status": "Склад - на заправку",
            "department": "ИТ отдел",
            "comment": "Резервный картридж"
        },
        {
            "name": "Картридж Brother HL-1110",
            "barcode": "CARTRIDGE004",
            "type": "Картридж",
            "status": "Склад - выдача",
            "department": "ИТ отдел",
            "comment": "Готов к выдаче"
        },
        # Computer Equipment
        {
            "name": "Ноутбук Dell Latitude 5420",
            "barcode": "COMP001",
            "type": "Комп. и орг. техника",
            "status": "МОЛ",
            "department": "Отдел продаж",
            "comment": "Основной ноутбук менеджера"
        },
        {
            "name": "Монитор LG 24MK430H",
            "barcode": "COMP002",
            "type": "Комп. и орг. техника",
            "status": "МОЛ",
            "department": "Бухгалтерия",
            "comment": "24 дюйма, Full HD"
        },
        {
            "name": "Принтер HP LaserJet Pro M404n",
            "barcode": "COMP003",
            "type": "Комп. и орг. техника",
            "status": "В ремонте",
            "department": None,
            "comment": "Неисправность блока питания"
        },
        {
            "name": "ПК Dell OptiPlex 3080",
            "barcode": "COMP004",
            "type": "Комп. и орг. техника",
            "status": "Склад",
            "department": "ИТ отдел",
            "comment": "Резервный компьютер"
        },
        {
            "name": "МФУ Canon i-SENSYS MF643Cdw",
            "barcode": "COMP005",
            "type": "Комп. и орг. техника",
            "status": "ИТ отдел",
            "department": "ИТ отдел",
            "comment": "Цветной лазерный МФУ"
        },
        {
            "name": "Планшет iPad Air",
            "barcode": "COMP006",
            "type": "Комп. и орг. техника",
            "status": "Перемещение",
            "department": "Отдел продаж",
            "comment": "Перемещен на склад для подготовки к выдаче"
        },
    ]
    
    for eq_data in test_equipment:
        equipment = db.query(Equipment).filter(Equipment.barcode == eq_data["barcode"]).first()
        if not equipment:
            status_key = f"{'cartridge' if eq_data['type'] == 'Картридж' else 'computer'}_{eq_data['status']}"
            equipment = Equipment(
                name=eq_data["name"],
                barcode=eq_data["barcode"],
                equipment_type_id=equipment_types[eq_data["type"]].id,
                status_id=statuses[status_key].id,
                department_id=departments[eq_data["department"]].id if eq_data["department"] else None,
                user_id=users["Иван Иванов"].id if eq_data["department"] else None,
                comment=eq_data["comment"],
                created_by_id=users["Администратор Системы"].id
            )
            db.add(equipment)
            
            # Commit to get equipment ID
            db.commit()
            db.refresh(equipment)
            
            # Create initial movement history entry
            movement = MovementHistory(
                equipment_id=equipment.id,
                status_id=statuses[status_key].id,
                department_id=equipment.department_id,
                user_id=users["Администратор Системы"].id,
                comment="Начальная запись"
            )
            db.add(movement)
    
    db.commit()
    print("Database initialized successfully with test data!")
