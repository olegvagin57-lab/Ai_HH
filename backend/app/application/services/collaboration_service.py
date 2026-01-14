"""Collaboration service for team work"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.entities.comment import Comment
from app.domain.entities.candidate import Candidate
from app.domain.entities.user import User
from app.domain.entities.search import Resume
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException, ValidationException
import re


logger = get_logger(__name__)


class CollaborationService:
    """Service for team collaboration features"""
    
    async def create_comment(
        self,
        resume_id: str,
        user: User,
        content: str,
        parent_comment_id: Optional[str] = None,
        is_internal: bool = True
    ) -> Comment:
        """Create a comment on a candidate"""
        # Verify resume exists
        resume = await Resume.get(resume_id)
        if not resume:
            raise NotFoundException("Resume not found")
        
        # Extract mentions from content (@username or @user_id)
        mentions = self._extract_mentions(content)
        
        comment = Comment(
            resume_id=resume_id,
            user_id=str(user.id),
            content=content,
            mentions=mentions,
            parent_comment_id=parent_comment_id,
            is_internal=is_internal
        )
        await comment.create()
        
        logger.info(
            "Comment created",
            comment_id=str(comment.id),
            resume_id=resume_id,
            user_id=str(user.id),
            mentions_count=len(mentions)
        )
        
        return comment
    
    async def get_comments(
        self,
        resume_id: str,
        limit: int = 50,
        include_replies: bool = True
    ) -> List[Comment]:
        """Get comments for a candidate"""
        if include_replies:
            # Get all comments (including replies)
            comments = await Comment.find(
                {"resume_id": resume_id}
            ).sort(Comment.created_at).limit(limit).to_list()
        else:
            # Get only top-level comments
            comments = await Comment.find(
                {"resume_id": resume_id, "parent_comment_id": None}
            ).sort(Comment.created_at).limit(limit).to_list()
        
        return comments
    
    async def update_comment(
        self,
        comment_id: str,
        user: User,
        content: str
    ) -> Comment:
        """Update a comment"""
        comment = await Comment.get(comment_id)
        if not comment:
            raise NotFoundException("Comment not found")
        
        # Check permissions
        if str(comment.user_id) != str(user.id) and not user.has_permission("comments:edit_all"):
            raise ValidationException("You can only edit your own comments")
        
        # Extract mentions
        mentions = self._extract_mentions(content)
        
        comment.content = content
        comment.mentions = mentions
        comment.updated_at = datetime.utcnow()
        await comment.save()
        
        logger.info("Comment updated", comment_id=comment_id)
        return comment
    
    async def delete_comment(
        self,
        comment_id: str,
        user: User
    ) -> None:
        """Delete a comment"""
        comment = await Comment.get(comment_id)
        if not comment:
            raise NotFoundException("Comment not found")
        
        # Check permissions
        if str(comment.user_id) != str(user.id) and not user.has_permission("comments:delete_all"):
            raise ValidationException("You can only delete your own comments")
        
        # Delete replies first
        replies = await Comment.find({"parent_comment_id": comment_id}).to_list()
        for reply in replies:
            await reply.delete()
        
        await comment.delete()
        
        logger.info("Comment deleted", comment_id=comment_id)
    
    async def get_activity_feed(
        self,
        user: Optional[User] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get activity feed for a user or all activities"""
        activities = []
        
        # Get recent comments
        query = {}
        if user:
            # Get comments on candidates assigned to user or where user is mentioned
            from app.domain.entities.candidate import Candidate
            assigned_candidates = await Candidate.find(
                {"assigned_to_user_id": str(user.id)}
            ).to_list()
            assigned_resume_ids = [c.resume_id for c in assigned_candidates]
            
            query = {
                "$or": [
                    {"resume_id": {"$in": assigned_resume_ids}},
                    {"mentions": str(user.id)},
                    {"user_id": str(user.id)}
                ]
            }
        
        comments = await Comment.find(query).sort(-Comment.created_at).limit(limit).to_list()
        
        for comment in comments:
            activities.append({
                "type": "comment",
                "id": str(comment.id),
                "resume_id": comment.resume_id,
                "user_id": comment.user_id,
                "content": comment.content[:100],  # Preview
                "created_at": comment.created_at.isoformat()
            })
        
        # Get status changes (from interactions)
        from app.domain.entities.candidate import Interaction
        interaction_query = {}
        if user:
            interaction_query = {
                "$or": [
                    {"user_id": str(user.id)},
                    {"action_data.assigned_to_user_id": str(user.id)}
                ]
            }
        
        interactions = await Interaction.find(interaction_query).sort(-Interaction.created_at).limit(limit).to_list()
        
        for interaction in interactions:
            activities.append({
                "type": interaction.action_type,
                "id": str(interaction.id),
                "resume_id": interaction.resume_id,
                "user_id": interaction.user_id,
                "action_data": interaction.action_data,
                "created_at": interaction.created_at.isoformat()
            })
        
        # Sort by created_at descending
        activities.sort(key=lambda x: x["created_at"], reverse=True)
        
        return activities[:limit]
    
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from content"""
        # Pattern: @username or @user_id
        mentions = []
        pattern = r'@(\w+)'
        matches = re.findall(pattern, content)
        
        # Try to resolve usernames to user IDs
        # For now, just return the matches (can be enhanced to resolve usernames)
        return matches
    
    async def get_candidate_ratings_summary(self, resume_id: str) -> Dict[str, Any]:
        """Get summary of ratings for a candidate"""
        candidate = await Candidate.find_one({"resume_id": resume_id})
        if not candidate:
            return {
                "average_rating": None,
                "total_ratings": 0,
                "ratings_breakdown": {}
            }
        
        # Count ratings by value
        ratings_breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in candidate.ratings.values():
            if 1 <= rating <= 5:
                ratings_breakdown[rating] = ratings_breakdown.get(rating, 0) + 1
        
        return {
            "average_rating": candidate.average_rating,
            "total_ratings": len(candidate.ratings),
            "ratings_breakdown": ratings_breakdown
        }


# Global service instance
collaboration_service = CollaborationService()
