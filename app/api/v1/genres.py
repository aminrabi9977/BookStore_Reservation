from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
# from pydantic import BaseModel
from app.database import get_db
from app.models.genre import Genre
from app.schemas.genre import GenreResponse

router = APIRouter(prefix="/genres", tags=["genres"])

@router.get("/", response_model=List[GenreResponse])
async def read_genres(skip: int = 0,limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Genre).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{genre_id}", response_model=GenreResponse)
async def read_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(Genre).where(Genre.id == genre_id)
    result = await db.execute(query)
    genre = result.scalar_one_or_none()
    
    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    return genre