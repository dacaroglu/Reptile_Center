# app/routers/ui.py
from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud

router = APIRouter(tags=["ui"])  # no prefix; "/" will be home

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Page shell; the summary table is pulled in via HTMX
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/ui/summary", response_class=HTMLResponse)
def ui_summary(request: Request, db: Session = Depends(get_db)):
    items = crud.latest_per_terrarium(db)
    return templates.TemplateResponse(
        "components/summary_table.html",
        {"request": request, "items": items},
    )

@router.get("/terrarium/{slug}", response_class=HTMLResponse)
def terrarium_detail(slug: str, request: Request):
    # Template fetches /api/v1/readings JSON and draws charts client-side
    return templates.TemplateResponse("terrarium.html", {"request": request, "slug": slug})
