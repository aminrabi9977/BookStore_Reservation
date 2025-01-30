from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.book import Book

class BookService:
    @staticmethod
    async def get_book(db: AsyncSession, 
        book_id: int) -> Optional[Book]:
        query = select(Book).where(Book.id == book_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_available_units(db: AsyncSession,
        book_id: int,
        change: int) -> Optional[Book]:
        book = await BookService.get_book(db, book_id)
        if book:
            book.adjust_available_units(change)
            await db.commit()
            await db.refresh(book)
        return book