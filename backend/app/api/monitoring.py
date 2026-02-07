from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.models.database import get_db
from app.models.models import MonitoringTarget
from app.schemas.schemas import (
    MonitoringTargetCreate,
    MonitoringTargetResponse,
    MonitoringTargetUpdate,
)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.post("/targets", response_model=MonitoringTargetResponse)
async def add_monitoring_target(
    target: MonitoringTargetCreate,
    db: Session = Depends(get_db),
):
    """Add a new monitoring target."""
    monitoring_target = MonitoringTarget(
        type=target.type,
        value=target.value,
        platform=target.platform,
        added_by=target.added_by,
    )

    db.add(monitoring_target)
    db.commit()
    db.refresh(monitoring_target)
    return monitoring_target


@router.get("/targets", response_model=List[MonitoringTargetResponse])
async def list_monitoring_targets(
    platform: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List monitoring targets with optional filtering.

    Parameters:
    - platform: Filter by platform (instagram, tiktok, etc.)
    - type: Filter by type (hashtag, account, keyword, etc.)
    - active: Filter by active status
    - limit: Max items to return
    - offset: Pagination offset
    """
    query = db.query(MonitoringTarget)

    if platform:
        query = query.filter(MonitoringTarget.platform == platform)
    if type:
        query = query.filter(MonitoringTarget.type == type)
    if active is not None:
        query = query.filter(MonitoringTarget.active == active)

    total = query.count()
    targets = query.order_by(desc(MonitoringTarget.added_at)).limit(limit).offset(offset).all()

    return targets


@router.get("/targets/{target_id}", response_model=MonitoringTargetResponse)
async def get_monitoring_target(
    target_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific monitoring target."""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Monitoring target not found")
    return target


@router.put("/targets/{target_id}", response_model=MonitoringTargetResponse)
async def update_monitoring_target(
    target_id: int,
    update: MonitoringTargetUpdate,
    db: Session = Depends(get_db),
):
    """Update a monitoring target."""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Monitoring target not found")

    if update.active is not None:
        target.active = update.active
    if update.value is not None:
        target.value = update.value

    db.commit()
    db.refresh(target)
    return target


@router.delete("/targets/{target_id}")
async def delete_monitoring_target(
    target_id: int,
    db: Session = Depends(get_db),
):
    """Delete a monitoring target."""
    target = db.query(MonitoringTarget).filter(MonitoringTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Monitoring target not found")

    db.delete(target)
    db.commit()

    return {"message": "Monitoring target deleted successfully"}
