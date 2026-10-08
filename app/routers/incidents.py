from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Incident, User
from ..schemas import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate
)
from .auth import get_current_user


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


# --------------------------------------------------
# CREATE INCIDENT
# --------------------------------------------------

@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
        assigned_to=incident_data.assigned_to
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


# --------------------------------------------------
# INCIDENT STATISTICS
# --------------------------------------------------

@router.get("/stats")
def get_incident_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(Incident).count()

    open_count = db.query(Incident).filter(
        Incident.status == "open"
    ).count()

    investigating_count = db.query(Incident).filter(
        Incident.status == "investigating"
    ).count()

    resolved_count = db.query(Incident).filter(
        Incident.status == "resolved"
    ).count()

    closed_count = db.query(Incident).filter(
        Incident.status == "closed"
    ).count()

    critical_count = db.query(Incident).filter(
        Incident.severity == "P1"
    ).count()

    return {
        "total": total,
        "open": open_count,
        "investigating": investigating_count,
        "resolved": resolved_count,
        "closed": closed_count,
        "critical": critical_count
    }


# --------------------------------------------------
# GET INCIDENTS
# WITH SEARCH, FILTERING AND PAGINATION
# --------------------------------------------------

@router.get(
    "/",
    response_model=list[IncidentResponse]
)
def get_incidents(
    search: str | None = Query(
        default=None,
        description="Search by incident title"
    ),

    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status"
    ),

    severity: str | None = Query(
        default=None,
        description="Filter by severity: P1, P2, P3 or P4"
    ),

    assigned_to: str | None = Query(
        default=None,
        description="Filter by assignee"
    ),

    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of incidents per page"
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Incident)

    # -----------------------------
    # Search
    # -----------------------------

    if search:
        query = query.filter(
            Incident.title.ilike(f"%{search}%")
        )

    # -----------------------------
    # Status filter
    # -----------------------------

    if status_filter:
        query = query.filter(
            Incident.status == status_filter
        )

    # -----------------------------
    # Severity filter
    # -----------------------------

    if severity:
        query = query.filter(
            Incident.severity == severity
        )

    # -----------------------------
    # Assigned user filter
    # -----------------------------

    if assigned_to:
        query = query.filter(
            Incident.assigned_to == assigned_to
        )

    # -----------------------------
    # Pagination
    # -----------------------------

    offset = (page - 1) * limit

    incidents = query.order_by(
        Incident.id.desc()
    ).offset(offset).limit(limit).all()

    return incidents


# --------------------------------------------------
# GET INCIDENT BY ID
# --------------------------------------------------

@router.get(
    "/{incident_id}",
    response_model=IncidentResponse
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return incident


# --------------------------------------------------
# UPDATE INCIDENT
# --------------------------------------------------

@router.put(
    "/{incident_id}",
    response_model=IncidentResponse
)
def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    if incident_data.status is not None:
        incident.status = incident_data.status

    if incident_data.severity is not None:
        incident.severity = incident_data.severity

    if incident_data.assigned_to is not None:
        incident.assigned_to = incident_data.assigned_to

    db.commit()
    db.refresh(incident)

    return incident


# --------------------------------------------------
# DELETE INCIDENT
# --------------------------------------------------

@router.delete(
    "/{incident_id}"
)
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    db.delete(incident)
    db.commit()

    return {
        "message": "Incident deleted successfully",
        "incident_id": incident_id
    }