from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.fcm import (
    SendNotificationRequest,
    SendMultipleNotificationRequest,
    SendTopicNotificationRequest,
    CustomMessageRequest,
    TopicSubscriptionRequest,
    TokenValidationRequest,
    FCMResponse,
    TokenValidationResponse
)
from app.services.fcm_service import FCMService
from app.core.security import verify_token
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fcm", tags=["FCM Notifications"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Dependency to get current authenticated user."""
    return verify_token(credentials.credentials)


@router.post("/send-notification", response_model=FCMResponse)
async def send_notification(
    request: SendNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send push notification to a single device token
    """
    try:
        fcm_service = FCMService()
        response = await fcm_service.send_to_token(
            token=request.token,
            title=request.title,
            body=request.body,
            data=request.data,
            image=request.image,
            click_action=request.click_action,
            link=request.link
        )
        
        return FCMResponse(
            success=True,
            message="Notification sent successfully",
            message_id=response.get("name") if response else None,
            data=response
        )
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return FCMResponse(
            success=False,
            message="Failed to send notification",
            error=str(e)
        )


@router.post("/send-multiple", response_model=FCMResponse)
async def send_multiple_notifications(
    request: SendMultipleNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send push notification to multiple device tokens
    """
    try:
        fcm_service = FCMService()
        response = await fcm_service.send_to_multiple_tokens(
            tokens=request.tokens,
            title=request.title,
            body=request.body,
            data=request.data,
            image=request.image,
            click_action=request.click_action,
            link=request.link
        )
        
        return FCMResponse(
            success=True,
            message=f"Notification sent to {len(request.tokens)} devices",
            data=response
        )
    except Exception as e:
        logger.error(f"Error sending multiple notifications: {str(e)}")
        return FCMResponse(
            success=False,
            message="Failed to send notifications",
            error=str(e)
        )


@router.post("/send-to-topic", response_model=FCMResponse)
async def send_topic_notification(
    request: SendTopicNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send push notification to a topic
    """
    try:
        fcm_service = FCMService()
        response = await fcm_service.send_to_topic(
            topic=request.topic,
            title=request.title,
            body=request.body,
            data=request.data,
            image=request.image,
            click_action=request.click_action
        )
        
        return FCMResponse(
            success=True,
            message=f"Notification sent to topic '{request.topic}'",
            message_id=response.get("name") if response else None,
            data=response
        )
    except Exception as e:
        logger.error(f"Error sending topic notification: {str(e)}")
        return FCMResponse(
            success=False,
            message="Failed to send topic notification",
            error=str(e)
        )


@router.post("/send-custom", response_model=FCMResponse)
async def send_custom_message(
    request: CustomMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send custom FCM message with full control over payload
    """
    try:
        fcm_service = FCMService()
        response = await fcm_service.send_custom_message(
            token=request.token,
            topic=request.topic,
            condition=request.condition,
            notification=request.notification,
            data=request.data,
            android=request.android,
            ios=request.ios,
            web=request.web
        )
        
        return FCMResponse(
            success=True,
            message="Custom message sent successfully",
            message_id=response.get("name") if response else None,
            data=response
        )
    except Exception as e:
        logger.error(f"Error sending custom message: {str(e)}")
        return FCMResponse(
            success=False,
            message="Failed to send custom message",
            error=str(e)
        )


@router.post("/subscribe-to-topic", response_model=FCMResponse)
async def subscribe_to_topic(
    request: TopicSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Subscribe device tokens to a topic
    """
    try:
        fcm_service = FCMService()
        response = await fcm_service.subscribe_to_topic(
            tokens=request.tokens,
            topic=request.topic
        )
        
        return FCMResponse(
            success=True,
            message=f"Successfully subscribed {len(request.tokens)} tokens to topic '{request.topic}'",
            data=response
        )
    except Exception as e:
        logger.error(f"Error subscribing to topic: {str(e)}")
        return FCMResponse(
            success=False,
            message="Failed to subscribe to topic",
            error=str(e)
        )


@router.post("/unsubscribe-from-topic", response_model=FCMResponse)
async def unsubscribe_from_topic(
    request: TopicSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Unsubscribe device tokens from a topic
    """
    try:
        fcm_service = FCMService()
        response = await fcm_service.unsubscribe_from_topic(
            tokens=request.tokens,
            topic=request.topic
        )
        
        return FCMResponse(
            success=True,
            message=f"Successfully unsubscribed {len(request.tokens)} tokens from topic '{request.topic}'",
            data=response
        )
    except Exception as e:
        logger.error(f"Error unsubscribing from topic: {str(e)}")
        return FCMResponse(
            success=False,
            message="Failed to unsubscribe from topic",
            error=str(e)
        )


@router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(
    request: TokenValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate an FCM device token
    """
    try:
        fcm_service = FCMService()
        is_valid, details = await fcm_service.validate_token(request.token)
        
        return TokenValidationResponse(
            token=request.token,
            is_valid=is_valid,
            details=details
        )
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return TokenValidationResponse(
            token=request.token,
            is_valid=False,
            details={"error": str(e)}
        )


@router.get("/health", response_model=dict)
async def fcm_health_check():
    """
    Check FCM service health
    """
    try:
        fcm_service = FCMService()
        # Check if service can initialize properly
        return {
            "status": "healthy",
            "service": "fcm",
            "message": "FCM service is operational"
        }
    except Exception as e:
        logger.error(f"FCM health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"FCM service unavailable: {str(e)}"
        )


@router.get("/check-permissions", response_model=dict)
async def check_fcm_permissions():
    """
    Check if the service account has proper FCM permissions
    """
    try:
        fcm_service = FCMService()
        permissions_check = fcm_service.check_service_account_permissions()
        
        if permissions_check.get("has_permissions"):
            return {
                "status": "success",
                "message": "Service account has proper FCM permissions",
                "details": permissions_check
            }
        else:
            return {
                "status": "error",
                "message": "Service account lacks proper FCM permissions",
                "details": permissions_check,
                "troubleshooting": {
                    "steps": [
                        "1. Go to Firebase Console > Project Settings > Service Accounts",
                        "2. Ensure the service account has 'Firebase Admin SDK' role",
                        "3. Verify the service account has 'Firebase Messaging Admin' permissions",
                        "4. Check if Firebase Cloud Messaging API is enabled in Google Cloud Console"
                    ]
                }
            }
    except Exception as e:
        logger.error(f"Error checking FCM permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check permissions: {str(e)}"
        )


@router.get("/project-info")
async def get_project_info():
    """
    Get Firebase project information for debugging SenderId mismatch issues
    """
    try:
        fcm_service = FCMService()
        project_info = fcm_service.get_project_info()
        
        return {
            "status": "success",
            "message": "Firebase project information",
            "project_info": project_info,
            "instructions": {
                "sender_id_mismatch_fix": [
                    f"Your client app must use SenderId (messagingSenderId): {project_info['sender_id']}",
                    f"Your client app must use Project ID: {project_info['project_id']}",
                    "Update your client app configuration (google-services.json for Android, Firebase config for Web)",
                    "Regenerate FCM registration tokens after updating configuration",
                    "Old tokens from different projects will not work"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting project info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project info: {str(e)}"
        )
