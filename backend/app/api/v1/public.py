from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db
from app.crud import page as crud_page
from app.schemas.page import PageWithBlocks

router = APIRouter()

@router.get("/pages/{page_id}", response_model=PageWithBlocks)
def get_public_page(
    page_id: UUID,
    db: Session = Depends(get_db)
):
    """Get public page details"""
    page = crud_page.get_by_id(db, page_id=page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    if not page.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found" # Hide that it exists but is private
        )
    
    return page
