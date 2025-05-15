from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .. import schemas, models, database
from ..utils import dependencies as deps

router = APIRouter(prefix="/lots", tags=["Lots"])

@router.post("/", response_model=schemas.LotResponse, status_code=status.HTTP_201_CREATED)
def create_lot(lot: schemas.LotCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_user)):
    try:
        new_lot = models.Lot(**lot.model_dump(), owner_id=current_user.id, current_price=lot.start_price)
        db.add(new_lot)
        db.commit()
        db.refresh(new_lot)
        return new_lot
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

@router.get("/", response_model=list[schemas.LotResponse])
def get_lots(skip: int = 0, limit: int = 100, active_only: bool = True, db: Session = Depends(database.get_db)):
    try:
        query = db.query(models.Lot)
        if active_only:
            query = query.filter(models.Lot.end_time > datetime.utcnow())
        return query.order_by(models.Lot.created_at.desc()).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

@router.get("/{lot_id}", response_model=schemas.LotResponse)
def get_lot(lot_id: int, db: Session = Depends(database.get_db)):
    try:
        lot = db.query(models.Lot).get(lot_id)
        if not lot:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Lot not found")
        return lot
    except SQLAlchemyError as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")

@router.delete("/{lot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lot(lot_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(deps.get_current_user)):
    try:
        lot = db.query(models.Lot).get(lot_id)
        if not lot:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Lot not found")
        if lot.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permission denied")
        db.delete(lot)
        db.commit()
        return
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")
