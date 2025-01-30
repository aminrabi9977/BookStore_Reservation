from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.city import City
from app.schemas.city import CityResponse

router = APIRouter(prefix="/cities", tags=["cities"])

@router.get("/", response_model=List[CityResponse])
async def read_cities(skip: int = 0,limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(City).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{city_id}", response_model=CityResponse)
async def read_city(
    city_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(City).where(City.id == city_id)
    result = await db.execute(query)
    city = result.scalar_one_or_none()
    
    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    return city