"""Candidate management service"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.entities.candidate import Candidate, Interaction
from app.domain.entities.search import Resume
from app.domain.entities.user import User
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException, ValidationException


logger = get_logger(__name__)


class CandidateService:
    """Service for managing candidates"""
    
    async def get_or_create_candidate(self, resume_id: str) -> Candidate:
        """Get existing candidate or create new one for a resume"""
        candidate = await Candidate.find_one({"resume_id": resume_id})
        if not candidate:
            candidate = Candidate(resume_id=resume_id, status="new")
            await candidate.create()
            logger.info("Created new candidate", resume_id=resume_id)
        return candidate
    
    async def get_candidate_by_resume_id(self, resume_id: str) -> Optional[Candidate]:
        """Get candidate by resume ID"""
        return await Candidate.find_one({"resume_id": resume_id})
    
    async def update_candidate_status(
        self,
        resume_id: str,
        new_status: str,
        user: User
    ) -> Candidate:
        """Update candidate status and log interaction"""
        valid_statuses = [
            "new", "reviewed", "shortlisted", "interview_scheduled",
            "interviewed", "offer_sent", "hired", "rejected", "on_hold"
        ]
        
        if new_status not in valid_statuses:
            raise ValidationException(f"Invalid status: {new_status}")
        
        candidate = await self.get_or_create_candidate(resume_id)
        old_status = candidate.status
        
        candidate.update_status(new_status)
        await candidate.save()
        
        # Log interaction
        await self._log_interaction(
            resume_id=resume_id,
            user_id=str(user.id),
            action_type="status_changed",
            action_data={
                "old_status": old_status,
                "new_status": new_status
            }
        )
        
        logger.info(
            "Candidate status updated",
            resume_id=resume_id,
            old_status=old_status,
            new_status=new_status,
            user_id=str(user.id)
        )
        
        return candidate
    
    async def add_tag(
        self,
        resume_id: str,
        tag: str,
        user: User
    ) -> Candidate:
        """Add a tag to a candidate"""
        candidate = await self.get_or_create_candidate(resume_id)
        candidate.add_tag(tag)
        await candidate.save()
        
        # Log interaction
        await self._log_interaction(
            resume_id=resume_id,
            user_id=str(user.id),
            action_type="tag_added",
            action_data={"tag": tag}
        )
        
        logger.info("Tag added to candidate", resume_id=resume_id, tag=tag)
        return candidate
    
    async def remove_tag(
        self,
        resume_id: str,
        tag: str,
        user: User
    ) -> Candidate:
        """Remove a tag from a candidate"""
        candidate = await self.get_or_create_candidate(resume_id)
        candidate.remove_tag(tag)
        await candidate.save()
        
        # Log interaction
        await self._log_interaction(
            resume_id=resume_id,
            user_id=str(user.id),
            action_type="tag_removed",
            action_data={"tag": tag}
        )
        
        logger.info("Tag removed from candidate", resume_id=resume_id, tag=tag)
        return candidate
    
    async def assign_to_user(
        self,
        resume_id: str,
        assigned_user_id: str,
        user: User
    ) -> Candidate:
        """Assign candidate to an HR specialist"""
        candidate = await self.get_or_create_candidate(resume_id)
        candidate.assigned_to_user_id = assigned_user_id
        candidate.updated_at = datetime.utcnow()
        await candidate.save()
        
        # Log interaction
        await self._log_interaction(
            resume_id=resume_id,
            user_id=str(user.id),
            action_type="assigned",
            action_data={"assigned_to_user_id": assigned_user_id}
        )
        
        logger.info(
            "Candidate assigned",
            resume_id=resume_id,
            assigned_to_user_id=assigned_user_id
        )
        return candidate
    
    async def add_rating(
        self,
        resume_id: str,
        rating: int,
        user: User
    ) -> Candidate:
        """Add or update a rating for a candidate"""
        if not (1 <= rating <= 5):
            raise ValidationException("Rating must be between 1 and 5")
        
        candidate = await self.get_or_create_candidate(resume_id)
        candidate.add_rating(str(user.id), rating)
        await candidate.save()
        
        # Log interaction
        await self._log_interaction(
            resume_id=resume_id,
            user_id=str(user.id),
            action_type="rating_added",
            action_data={"rating": rating}
        )
        
        logger.info(
            "Rating added to candidate",
            resume_id=resume_id,
            rating=rating,
            user_id=str(user.id)
        )
        return candidate
    
    async def update_notes(
        self,
        resume_id: str,
        notes: str,
        user: User
    ) -> Candidate:
        """Update candidate notes"""
        candidate = await self.get_or_create_candidate(resume_id)
        candidate.notes = notes
        candidate.updated_at = datetime.utcnow()
        await candidate.save()
        
        # Log interaction
        await self._log_interaction(
            resume_id=resume_id,
            user_id=str(user.id),
            action_type="notes_updated",
            action_data={"notes_length": len(notes)}
        )
        
        logger.info("Candidate notes updated", resume_id=resume_id)
        return candidate
    
    async def set_folder(
        self,
        resume_id: str,
        folder: Optional[str],
        user: User
    ) -> Candidate:
        """Set candidate folder"""
        candidate = await self.get_or_create_candidate(resume_id)
        candidate.folder = folder
        candidate.updated_at = datetime.utcnow()
        await candidate.save()
        
        # Log interaction
        await self._log_interaction(
            resume_id=resume_id,
            user_id=str(user.id),
            action_type="folder_changed",
            action_data={"folder": folder}
        )
        
        logger.info("Candidate folder updated", resume_id=resume_id, folder=folder)
        return candidate
    
    async def get_interactions(
        self,
        resume_id: str,
        limit: int = 50
    ) -> List[Interaction]:
        """Get interaction history for a candidate"""
        interactions = await Interaction.find(
            {"resume_id": resume_id}
        ).sort(-Interaction.created_at).limit(limit).to_list()
        
        return interactions
    
    async def _log_interaction(
        self,
        resume_id: str,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> None:
        """Log an interaction"""
        interaction = Interaction(
            resume_id=resume_id,
            user_id=user_id,
            action_type=action_type,
            action_data=action_data
        )
        await interaction.create()
    
    async def get_all_candidates(
        self,
        user: Optional[User] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get all candidates with pagination"""
        query_dict = {}
        
        # Filter by assigned user if not admin
        if user and not user.can_view_all_searches():
            query_dict["assigned_to_user_id"] = str(user.id)
        
        skip = (page - 1) * page_size
        candidates = await Candidate.find(query_dict).sort(-Candidate.updated_at).skip(skip).limit(page_size).to_list()
        total = await Candidate.find(query_dict).count()
        
        return {
            "candidates": candidates,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_candidates_by_status(
        self,
        status: str,
        user: Optional[User] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get candidates by status with pagination"""
        query_dict = {"status": status}
        
        # Filter by assigned user if not admin
        if user and not user.can_view_all_searches():
            query_dict["assigned_to_user_id"] = str(user.id)
        
        skip = (page - 1) * page_size
        candidates = await Candidate.find(query_dict).sort(-Candidate.updated_at).skip(skip).limit(page_size).to_list()
        total = await Candidate.find(query_dict).count()
        
        return {
            "candidates": candidates,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_candidates_by_tags(
        self,
        tags: List[str],
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get candidates by tags"""
        query_dict = {"tags": {"$in": tags}}
        
        skip = (page - 1) * page_size
        candidates = await Candidate.find(query_dict).sort(-Candidate.updated_at).skip(skip).limit(page_size).to_list()
        total = await Candidate.find(query_dict).count()
        
        return {
            "candidates": candidates,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def detect_duplicates(self, resume: Resume) -> List[Resume]:
        """Detect duplicate resumes by email or phone"""
        duplicates = []
        
        # Extract email and phone from raw_data
        raw_data = resume.raw_data or {}
        email = raw_data.get("email") or raw_data.get("contact", {}).get("email")
        phone = raw_data.get("phone") or raw_data.get("contact", {}).get("phone")
        
        if email:
            # Search for resumes with same email
            matching_resumes = await Resume.find({
                "raw_data.email": email,
                "id": {"$ne": resume.id}
            }).to_list()
            duplicates.extend(matching_resumes)
        
        if phone:
            # Search for resumes with same phone
            matching_resumes = await Resume.find({
                "$or": [
                    {"raw_data.phone": phone},
                    {"raw_data.contact.phone": phone}
                ],
                "id": {"$ne": resume.id}
            }).to_list()
            duplicates.extend(matching_resumes)
        
        # Remove duplicates from list
        seen_ids = set()
        unique_duplicates = []
        for dup in duplicates:
            if str(dup.id) not in seen_ids:
                seen_ids.add(str(dup.id))
                unique_duplicates.append(dup)
        
        return unique_duplicates


# Global service instance
candidate_service = CandidateService()
