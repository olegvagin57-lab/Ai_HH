"""Export service for search results"""
from typing import List
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
import csv
from app.domain.entities.search import Search, Resume
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException


logger = get_logger(__name__)


class ExportService:
    """Service for exporting search results"""
    
    async def export_to_excel(self, search_id: str) -> BytesIO:
        """Export search results to Excel"""
        # Get search
        search = await Search.get(search_id)
        if not search:
            raise NotFoundException("Search not found")
        
        # Get all resumes
        resumes = await Resume.find({"search_id": str(search.id)}).sort(-Resume.ai_score).to_list()
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Resumes"
        
        # Headers
        headers = [
            "ID", "HH ID", "Name", "Age", "City", "Title", "Salary", "Currency",
            "Preliminary Score", "AI Score", "AI Summary", "AI Questions", "AI Generated",
            "Analyzed"
        ]
        ws.append(headers)
        
        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")
        
        # Add data
        for resume in resumes:
            row = [
                str(resume.id),
                resume.hh_id or "",
                resume.name or "",
                resume.age or "",
                resume.city or "",
                resume.title or "",
                resume.salary or "",
                resume.currency or "",
                resume.preliminary_score or "",
                resume.ai_score or "",
                resume.ai_summary or "",
                "; ".join(resume.ai_questions) if resume.ai_questions else "",
                "Yes" if resume.ai_generated_detected else "No",
                "Yes" if resume.analyzed else "No"
            ]
            ws.append(row)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    logger.debug("Error calculating column width", error=str(e))
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        logger.info("Excel export created", search_id=search_id, resumes_count=len(resumes))
        
        return output
    
    async def export_to_csv(self, search_id: str) -> BytesIO:
        """Export search results to CSV"""
        # Get search
        search = await Search.get(search_id)
        if not search:
            raise NotFoundException("Search not found")
        
        # Get all resumes
        resumes = await Resume.find({"search_id": str(search.id)}).sort(-Resume.ai_score).to_list()
        
        # Create CSV
        output = BytesIO()
        writer = csv.writer(output)
        
        # Headers
        headers = [
            "ID", "HH ID", "Name", "Age", "City", "Title", "Salary", "Currency",
            "Preliminary Score", "AI Score", "AI Summary", "AI Questions", "AI Generated",
            "Analyzed"
        ]
        writer.writerow(headers)
        
        # Add data
        for resume in resumes:
            row = [
                str(resume.id),
                resume.hh_id or "",
                resume.name or "",
                resume.age or "",
                resume.city or "",
                resume.title or "",
                resume.salary or "",
                resume.currency or "",
                resume.preliminary_score or "",
                resume.ai_score or "",
                resume.ai_summary or "",
                "; ".join(resume.ai_questions) if resume.ai_questions else "",
                "Yes" if resume.ai_generated_detected else "No",
                "Yes" if resume.analyzed else "No"
            ]
            writer.writerow(row)
        
        output.seek(0)
        
        logger.info("CSV export created", search_id=search_id, resumes_count=len(resumes))
        
        return output


# Global service instance
export_service = ExportService()
