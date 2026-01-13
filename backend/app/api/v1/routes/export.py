"""Export API routes"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from app.application.services.export_service import export_service
from app.application.services.search_service import search_service
from app.api.middleware.auth import get_current_active_user, require_permission
from app.domain.entities.user import User
from app.core.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/search", tags=["export"])


@router.get("/{search_id}/export/excel")
async def export_search_to_excel(
    search_id: str,
    current_user: User = Depends(require_permission("search:export"))
):
    """Export search results to Excel"""
    # Check access
    await search_service.get_search(search_id, current_user)
    
    # Generate Excel file
    excel_file = await export_service.export_to_excel(search_id)
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="search_{search_id}_results.xlsx"'
        }
    )


@router.get("/{search_id}/export/csv")
async def export_search_to_csv(
    search_id: str,
    current_user: User = Depends(require_permission("search:export"))
):
    """Export search results to CSV"""
    # Check access
    await search_service.get_search(search_id, current_user)
    
    # Generate CSV file
    csv_file = await export_service.export_to_csv(search_id)
    
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="search_{search_id}_results.csv"'
        }
    )
