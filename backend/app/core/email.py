import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending notifications.

    Currently logs emails to console.
    TODO: Implement actual email sending using SendGrid, AWS SES, or SMTP.
    """

    @staticmethod
    def send_invitation_email(
        recipient_email: str,
        workspace_name: str,
        inviter_name: str,
        invitation_token: str,
        role: str
    ) -> bool:
        """
        Send workspace invitation email.

        Args:
            recipient_email: Email address of the invitee
            workspace_name: Name of the workspace
            inviter_name: Name of the person who sent the invitation
            invitation_token: Unique token for accepting the invitation
            role: Role assigned to the invitee

        Returns:
            bool: True if email was sent successfully
        """
        # In production, this URL would point to your frontend
        # For now, we'll construct a simple URL
        accept_url = f"{settings.FRONTEND_URL}/accept-invitation?token={invitation_token}"

        email_subject = f"{inviter_name} invited you to join {workspace_name}"
        email_body = f"""
Hi!

{inviter_name} has invited you to join the workspace "{workspace_name}" as a {role}.

To accept this invitation, click the link below:
{accept_url}

Or use this token manually: {invitation_token}

This invitation will expire in 7 days.

---
Notion Clone
        """

        # TODO: Implement actual email sending
        # For now, just log the email
        logger.info("=" * 60)
        logger.info("SENDING EMAIL (simulated)")
        logger.info(f"To: {recipient_email}")
        logger.info(f"Subject: {email_subject}")
        logger.info(f"Body:\n{email_body}")
        logger.info("=" * 60)

        return True

    @staticmethod
    def send_member_removed_email(
        recipient_email: str,
        workspace_name: str,
        remover_name: str
    ) -> bool:
        """
        Send notification when a member is removed from a workspace.

        Args:
            recipient_email: Email of the removed member
            workspace_name: Name of the workspace
            remover_name: Name of the person who removed them

        Returns:
            bool: True if email was sent successfully
        """
        email_subject = f"You've been removed from {workspace_name}"
        email_body = f"""
Hi,

You have been removed from the workspace "{workspace_name}" by {remover_name}.

You no longer have access to this workspace.

---
Notion Clone
        """

        logger.info("=" * 60)
        logger.info("SENDING EMAIL (simulated)")
        logger.info(f"To: {recipient_email}")
        logger.info(f"Subject: {email_subject}")
        logger.info(f"Body:\n{email_body}")
        logger.info("=" * 60)

        return True

    @staticmethod
    def send_role_changed_email(
        recipient_email: str,
        workspace_name: str,
        old_role: str,
        new_role: str,
        changer_name: str
    ) -> bool:
        """
        Send notification when a member's role changes.

        Args:
            recipient_email: Email of the member
            workspace_name: Name of the workspace
            old_role: Previous role
            new_role: New role
            changer_name: Name of the person who changed the role

        Returns:
            bool: True if email was sent successfully
        """
        email_subject = f"Your role in {workspace_name} has changed"
        email_body = f"""
Hi,

Your role in the workspace "{workspace_name}" has been changed by {changer_name}.

Previous role: {old_role}
New role: {new_role}

---
Notion Clone
        """

        logger.info("=" * 60)
        logger.info("SENDING EMAIL (simulated)")
        logger.info(f"To: {recipient_email}")
        logger.info(f"Subject: {email_subject}")
        logger.info(f"Body:\n{email_body}")
        logger.info("=" * 60)

        return True


# Singleton instance
email_service = EmailService()
