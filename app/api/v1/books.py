from app.database import get_db
from app.models.book import Book
from app.schemas.books import BookCreate, BookUpdate, BookResponse


from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from typing import Optional,List

router = APIRouter( prefix="/books", tags=["Books"])

@router.get("/{book_id}", response_model = BookResponse)
async def get_book(
    book_id = int,
    db: AsyncSession = Depends(get_db),
):
    query = select(Book).options(selectinload(Book.authors)).where(Book.id == book_id)
    result = await db.execute(query)
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUNT,
                            detail = "Book not founf")
        return book


@router.get("/" , response_model = List[BookResponse]) 
async def get_books(skip: int = 0, limit: int =100, genre_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    query = select(Book).options(selectinload(Book.authors))
    if genre_id:
        query = query.where(Book.genre_id == genre_id)

    query = query.offset(skip).limit(limit)     
    result = await db.execute(query)
    books = result.scalars().all 
    return books   

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    db: AsyncSession = Depends(get_db)
):
   
    query = select(Book).where(Book.isbn == book.isbn)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISBN already registered"
        )
    
    db_book = Book(
        title=book.title,
        isbn=book.isbn,
        price=book.price,
        genre_id=book.genre_id,
        description=book.description,
        total_units=book.total_units,
        available_units=book.total_units
    )
    
    db.add(db_book)
    await db.flush()

    
    if book.author_ids:
        author_query = select(Author).where(Author.id.in_(book.author_ids))
        result = await db.execute(author_query)
        authors = result.scalars().all()
        db_book.authors.extend(authors)

    await db.commit()
    await db.refresh(db_book)
    return db_book      

@router.put("/{book_id)}", response_model= BookResponse)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Book).where(Book.id == book_id)
    result = await db.execute(query)
    db_book = result.scalar_one_or_none()

    if db_book is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUNT, detail = "Book not found")

    update_data = book_update.dict(exclude_unset = True)

    if 'author_ids' in update_data:
        author_ids = update_data.pop('author_ids')
        author_query = select(Author).where(Author.id.in_(author_ids))
        result = await db.execute(author_query)
        authors = result.scalars().all()
        db_book.authors = authors

    for key, value in update_data.items():
        setattr(db_book, key, value)

    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)
):
    query = select(Book).where(Book.id == book_id)
    result = await db.execute(query)
    db_book = result.scalar_one_or_none()
    
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
        
    await db.delete(db_book)
    await db.commit()