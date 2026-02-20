from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.calendar_entry import CalendarEntry
from app.schemas.calendar import CalendarEntryCreate, CalendarEntryUpdate, CalendarEntryResponse

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("", response_model=list[CalendarEntryResponse])
async def list_calendar_entries(
    month: int | None = None,
    year: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CalendarEntry).order_by(CalendarEntry.scheduled_date)
    if month and year:
        from sqlalchemy import extract
        query = query.where(
            extract("month", CalendarEntry.scheduled_date) == month,
            extract("year", CalendarEntry.scheduled_date) == year,
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=CalendarEntryResponse, status_code=201)
async def create_calendar_entry(data: CalendarEntryCreate, db: AsyncSession = Depends(get_db)):
    entry = CalendarEntry(**data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/{entry_id}", response_model=CalendarEntryResponse)
async def update_calendar_entry(
    entry_id: UUID, data: CalendarEntryUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CalendarEntry).where(CalendarEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Calendar entry not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_calendar_entry(entry_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CalendarEntry).where(CalendarEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Calendar entry not found")
    await db.delete(entry)
    await db.commit()
