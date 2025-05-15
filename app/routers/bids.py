from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, database, utils

router = APIRouter(prefix="/bids", tags=["bids"])


@router.post("/", response_model=schemas.BidResponse)
def create_bid(
        bid: schemas.BidCreate,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(utils.get_current_user)
):
    lot = db.query(models.Lot).get(bid.lot_id)
    if not lot:
        raise HTTPException(404, "lot not found")

    if bid.amount <= lot.current_price:
        raise HTTPException(400, "bid must be higher than current price")

    new_bid = models.Bid(
        amount=bid.amount,
        user_id=current_user.id,
        lot_id=bid.lot_id
    )

    lot.current_price = bid.amount

    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)
    return new_bid
