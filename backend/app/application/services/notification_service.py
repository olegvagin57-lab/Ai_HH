"""Notification service"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.entities.notification import Notification
from app.domain.entities.user import User
from app.core.logging import get_logger


logger = get_logger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )
        await notification.create()
        
        logger.info(
            "Notification created",
            notification_id=str(notification.id),
            user_id=user_id,
            type=notification_type
        )
        
        return notification
    
    async def notify_new_candidate(
        self,
        user_id: str,
        resume_id: str,
        candidate_name: str,
        ai_score: int,
        vacancy_title: Optional[str] = None
    ) -> Notification:
        """Notify about a new suitable candidate"""
        title = "Новый подходящий кандидат"
        if vacancy_title:
            message = f"Найден новый кандидат для вакансии '{vacancy_title}': {candidate_name} (AI Score: {ai_score}/10)"
        else:
            message = f"Найден новый подходящий кандидат: {candidate_name} (AI Score: {ai_score}/10)"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="new_candidate",
            title=title,
            message=message,
            data={"resume_id": resume_id, "ai_score": ai_score, "vacancy_title": vacancy_title}
        )
    
    async def notify_auto_match_found(
        self,
        user_id: str,
        vacancy_id: str,
        vacancy_title: str,
        candidates_count: int
    ) -> Notification:
        """Notify about new candidates found via auto-matching"""
        title = "Автоматический подбор: найдены кандидаты"
        message = f"Для вакансии '{vacancy_title}' найдено {candidates_count} новых подходящих кандидатов"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="auto_match_found",
            title=title,
            message=message,
            data={"vacancy_id": vacancy_id, "candidates_count": candidates_count}
        )
    
    async def notify_status_changed(
        self,
        user_id: str,
        resume_id: str,
        candidate_name: str,
        old_status: str,
        new_status: str
    ) -> Notification:
        """Notify about candidate status change"""
        title = "Изменение статуса кандидата"
        message = f"Статус кандидата {candidate_name} изменен: {old_status} → {new_status}"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="status_changed",
            title=title,
            message=message,
            data={"resume_id": resume_id, "old_status": old_status, "new_status": new_status}
        )
    
    async def notify_comment_added(
        self,
        user_id: str,
        resume_id: str,
        candidate_name: str,
        commenter_name: str
    ) -> Notification:
        """Notify about new comment"""
        title = "Новый комментарий"
        message = f"{commenter_name} оставил комментарий к кандидату {candidate_name}"
        
        return await self.create_notification(
            user_id=user_id,
            notification_type="comment_added",
            title=title,
            message=message,
            data={"resume_id": resume_id, "commenter_name": commenter_name}
        )
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        page: int = 1
    ) -> Dict[str, Any]:
        """Get notifications for a user"""
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        skip = (page - 1) * limit
        notifications = await Notification.find(query).sort(-Notification.created_at).skip(skip).limit(limit).to_list()
        total = await Notification.find(query).count()
        
        return {
            "notifications": notifications,
            "total": total,
            "page": page,
            "limit": limit,
            "unread_count": await Notification.find({"user_id": user_id, "read": False}).count()
        }
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> Notification:
        """Mark notification as read"""
        notification = await Notification.get(notification_id)
        if not notification:
            raise NotFoundException("Notification not found")
        
        if str(notification.user_id) != str(user_id):
            raise ValidationException("Access denied")
        
        notification.mark_as_read()
        await notification.save()
        
        return notification
    
    async def mark_all_as_read(
        self,
        user_id: str
    ) -> int:
        """Mark all notifications as read for a user"""
        notifications = await Notification.find({"user_id": user_id, "read": False}).to_list()
        
        count = 0
        for notification in notifications:
            notification.mark_as_read()
            await notification.save()
            count += 1
        
        logger.info("All notifications marked as read", user_id=user_id, count=count)
        return count
    
    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> None:
        """Delete a notification"""
        notification = await Notification.get(notification_id)
        if not notification:
            raise NotFoundException("Notification not found")
        
        if str(notification.user_id) != str(user_id):
            raise ValidationException("Access denied")
        
        await notification.delete()
        
        logger.info("Notification deleted", notification_id=notification_id)


# Global service instance
notification_service = NotificationService()
