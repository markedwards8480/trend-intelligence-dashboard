from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.models.database import get_db
from app.models.models import MoodBoard, TrendItem
from app.schemas.schemas import (
    MoodBoardCreate,
    MoodBoardResponse,
    MoodBoardUpdate,
)

router = APIRouter(prefix="/api/moodboards", tags=["moodboards"])


@router.post("", response_model=MoodBoardResponse)
async def create_moodboard(
    moodboard: MoodBoardCreate,
    db: Session = Depends(get_db),
):
    """Create a new mood board."""
    # Verify all items exist
    if moodboard.item_ids:
        items = db.query(TrendItem).filter(TrendItem.id.in_(moodboard.item_ids)).all()
        if len(items) != len(moodboard.item_ids):
            raise HTTPException(status_code=400, detail="One or more trend items not found")

    board = MoodBoard(
        title=moodboard.title,
        description=moodboard.description,
        created_by=moodboard.created_by,
        category=moodboard.category,
        items=moodboard.item_ids,
    )

    db.add(board)
    db.commit()
    db.refresh(board)
    return board


@router.get("", response_model=List[MoodBoardResponse])
async def list_moodboards(
    created_by: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List all mood boards with optional filtering.

    Parameters:
    - created_by: Filter by creator
    - category: Filter by category
    - limit: Max items to return
    - offset: Pagination offset
    """
    query = db.query(MoodBoard)

    if created_by:
        query = query.filter(MoodBoard.created_by == created_by)
    if category:
        query = query.filter(MoodBoard.category == category)

    total = query.count()
    boards = query.order_by(desc(MoodBoard.created_at)).limit(limit).offset(offset).all()

    return boards


@router.get("/{board_id}", response_model=MoodBoardResponse)
async def get_moodboard(
    board_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific mood board with its trend items."""
    board = db.query(MoodBoard).filter(MoodBoard.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Mood board not found")

    # Fetch related trend items
    if board.items:
        trend_items = db.query(TrendItem).filter(TrendItem.id.in_(board.items)).all()
        board.trend_items = trend_items

    return board


@router.put("/{board_id}", response_model=MoodBoardResponse)
async def update_moodboard(
    board_id: int,
    update: MoodBoardUpdate,
    db: Session = Depends(get_db),
):
    """Update a mood board."""
    board = db.query(MoodBoard).filter(MoodBoard.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Mood board not found")

    # Verify items exist if provided
    if update.items is not None:
        items = db.query(TrendItem).filter(TrendItem.id.in_(update.items)).all()
        if len(items) != len(update.items):
            raise HTTPException(status_code=400, detail="One or more trend items not found")
        board.items = update.items

    if update.title is not None:
        board.title = update.title
    if update.description is not None:
        board.description = update.description
    if update.category is not None:
        board.category = update.category

    db.commit()
    db.refresh(board)
    return board


@router.delete("/{board_id}")
async def delete_moodboard(
    board_id: int,
    db: Session = Depends(get_db),
):
    """Delete a mood board."""
    board = db.query(MoodBoard).filter(MoodBoard.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Mood board not found")

    db.delete(board)
    db.commit()

    return {"message": "Mood board deleted successfully"}
