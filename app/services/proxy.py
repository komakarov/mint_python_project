from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app import models

def process_proxy_bids(lot_id: int, db: Session):
    while True:
        with db.begin():
            lot = db.execute(
                select(models.Lot)
                .where(models.Lot.id == lot_id)
                .with_for_update()
            ).scalar_one()

            top_bid = db.execute(
                select(models.Bid)
                .where(
                    (models.Bid.lot_id == lot_id) &
                    (models.Bid.is_proxy == True) &
                    (models.Bid.max_bid > lot.current_price)
                )
                .order_by(models.Bid.max_bid.desc())
            ).first()

            if not top_bid:
                break


            new_price = min(
                top_bid.max_bid,
                lot.current_price + lot.bid_step
            )


            db.execute(
                update(models.Lot)
                .where(models.Lot.id == lot_id)
                .values(current_price=new_price)
            )

            new_bid = models.Bid(
                amount=new_price,
                user_id=top_bid.user_id,
                lot_id=lot_id,
                is_proxy=True,
                max_bid=top_bid.max_bid
            )
            db.add(new_bid)
