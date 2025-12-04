from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud import workspace as crud_workspace
from app.crud import search as crud_search
from app.schemas.search import SearchQuery, SearchResponse
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=SearchResponse)
def search(
    search_query: SearchQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Full-text search across pages and blocks in a workspace.

    - **query**: Search text (1-500 characters)
    - **workspace_id**: Workspace to search in
    - **type_filter**: Optional filter by content type (pages_only, paragraph, etc.)
    - **include_archived**: Include archived pages (default: false)
    - **limit**: Max results (1-100, default: 20)
    - **offset**: Pagination offset (default: 0)

    Returns results grouped by page with relevance ranking and highlighted matches.
    """
    # Verify workspace exists
    workspace = crud_workspace.get_by_id(db, workspace_id=search_query.workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Verify user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=search_query.workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Execute search
    results, total, execution_time = crud_search.search_workspace(db, search_query)

    # Build response
    return SearchResponse(
        results=results,
        total=total,
        query=search_query.query,
        execution_time_ms=execution_time
    )
