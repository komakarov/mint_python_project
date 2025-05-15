from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, database
from ..utils import dependencies as deps

router = APIRouter(prefix="/bids", tags=["bids"])


@router.post("/", response_model=schemas.BidResponse, status_code=201)
def create_bid(
        bid: schemas.BidCreate,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    lot = db.query(models.Lot).get(bid.lot_id)
    if not lot:
        raise HTTPException(404, "lot not found")

    if bid.amount <= lot.current_price:
        raise HTTPException(400, "bid must be higher than current price")

    new_bid = models.Bid(
        amount=bid.amount,
        user_id=current_user.id,
        lot_id=bid.lot_id,
        is_proxy=bid.is_proxy,
        max_bid=bid.max_bid if bid.is_proxy else None
    )

    lot.current_price = bid.amount

    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)
    return new_bid
