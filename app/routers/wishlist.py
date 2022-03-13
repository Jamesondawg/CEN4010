from fastapi import Depends, status, HTTPException, APIRouter

from typing import List

from sqlalchemy.orm import Session
from db.database import get_db

import models.wishlist as models, schemas.wishlist as schemas
import utils, oauth2

MAX_ALLOWED_WISHLIST = 3

router = APIRouter(
    prefix = '/api/wishlist',
    tags=['Wish List Management']
)

@router.post('/{username}')
def create_wish_list(username, new_wish_list: schemas.WishList, db: Session = Depends(get_db)):
    existing_wishlist = db.query(models.WishList).filter(models.WishList.owner_username == username).all()
    if len(existing_wishlist) < MAX_ALLOWED_WISHLIST:
            wish_list = models.WishList(
                name = new_wish_list.name,
                books = new_wish_list.books,
                owner_username = username
            )
            for wishlist in existing_wishlist:
                if wishlist.name == wish_list.name:
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Wishlist name already exists => {wish_list.name}')
            db.add(wish_list)
            db.commit()
            db.refresh(wish_list)
            return {'detail': f'Wish List created for {wish_list.owner_username}'}
    else:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Could not create wish list => Wishlist limit reached!')

@router.get('/{username}', response_model=List[schemas.ShowWishList])
def get_wish_list(username, db: Session = Depends(get_db)):
    wish_list = db.query(models.WishList).filter(models.WishList.owner_username == username).all()
    if not wish_list:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'Could not find wish list that belongs to {username}')
    return wish_list