from fastapi import APIRouter, Query
from typing import List, Optional

from weather_alerts.models.Alert import Alert

router = APIRouter()

# Temporary in-memory storage
alerts_db: List[Alert] = []


@router.get("/", response_model=List[Alert])
async def get_alerts(
        user_id: Optional[str] = Query(None, description="Filter by user ID"),
        limit: int = Query(100, ge=1, le=1000, description="Max number of alerts to return"),
        offset: int = Query(0, ge=0, description="Number of alerts to skip")
):
    """
    Get alert history.

    - **user_id**: Optional filter to get alerts for specific user
    - **limit**: Maximum alerts to return
    - **offset**: Pagination offset
    """
    filtered_alerts = alerts_db

    if user_id:
        filtered_alerts = [alert for alert in alerts_db if alert.user_id == user_id]

    return filtered_alerts[offset:offset + limit]


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """Get a specific alert by ID"""
    for alert in alerts_db:
        if alert.alert_id == alert_id:
            return alert

    from fastapi import HTTPException, status
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Alert not found"
    )