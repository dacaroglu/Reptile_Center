from __future__ import annotations
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
from ..models import SensorRoleName

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/terrarium/{slug}", response_class=HTMLResponse)
def admin_map(slug: str, request: Request, db: Session = Depends(get_db)):
    seen = crud.list_seen_sensors(db, slug)
    role_map = crud.get_role_map(db, slug)
    return templates.TemplateResponse(
        "admin_map.html",
        {"request": request, "slug": slug, "seen": seen, "role_map": role_map, "roles": list(SensorRoleName)}
    )

@router.post("/admin/terrarium/{slug}/map", response_class=HTMLResponse)
def admin_set_map(slug: str, request: Request, role: str = Form(...), entity_id: str = Form(...), db: Session = Depends(get_db)):
    crud.set_role(db, terrarium_slug=slug, role=SensorRoleName(role), entity_id=entity_id)
    seen = crud.list_seen_sensors(db, slug)
    role_map = crud.get_role_map(db, slug)
    return templates.TemplateResponse(
        "components/role_table.html",
        {"request": request, "slug": slug, "seen": seen, "role_map": role_map, "roles": list(SensorRoleName)}
    )
