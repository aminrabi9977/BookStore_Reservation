from fastapi import HTTPException, status
from typing import Optional
from app.models.user import User
from app.models.book import Book

async def validate_owner(user: User, resource_owner_id: int) -> None:
    if user.role != "admin" and user.id != resource_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this resource"
        )

async def validate_book_author(user: User, book: Book) -> None:
    if user.role != "admin" and user.id not in [author.user_id for author in book.authors]:
        raise HTTPException(sstatus_code=status.HTTP_403_FORBIDDEN,
            detail="Only book authors can modify this resource"
        )