from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class SendNotificationRequest(BaseModel):
    """Single token notification request"""
    token: str = Field(..., description="FCM device token")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Optional[Dict[str, str]] = Field(None, description="Custom data payload")
    image: Optional[str] = Field(None, description="Image URL for notification")
    click_action: Optional[str] = Field(None, description="Action when notification is clicked")
    link: Optional[str] = Field(None, description="Web link to open")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eXQJ8V9K5fD:APA91bH...",
                "title": "Eraspace Member is Detected!",
                "body": "Open Information",
                "link": "https://erabeacon-7e08e.web.app/",
                "data": {
                    "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
                    "user_id": "user123"
                }
            }
        }


class SendMultipleNotificationRequest(BaseModel):
    """Multiple tokens notification request"""
    tokens: List[str] = Field(..., description="List of FCM device tokens")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Optional[Dict[str, str]] = Field(None, description="Custom data payload")
    image: Optional[str] = Field(None, description="Image URL for notification")
    click_action: Optional[str] = Field(None, description="Action when notification is clicked")
    link: Optional[str] = Field(None, description="Web link to open")

    class Config:
        json_schema_extra = {
            "example": {
                "tokens": ["token1", "token2", "token3"],
                "title": "Broadcast Message",
                "body": "Important announcement",
                "data": {
                    "type": "broadcast",
                    "priority": "high"
                }
            }
        }


class SendTopicNotificationRequest(BaseModel):
    """Topic notification request"""
    topic: str = Field(..., description="FCM topic name")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Optional[Dict[str, str]] = Field(None, description="Custom data payload")
    image: Optional[str] = Field(None, description="Image URL for notification")
    click_action: Optional[str] = Field(None, description="Action when notification is clicked")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "news",
                "title": "Breaking News",
                "body": "Important update available",
                "data": {
                    "category": "news",
                    "article_id": "123"
                }
            }
        }


class CustomMessageRequest(BaseModel):
    """Custom FCM message request"""
    token: Optional[str] = Field(None, description="FCM device token")
    topic: Optional[str] = Field(None, description="FCM topic")
    condition: Optional[str] = Field(None, description="FCM condition")
    notification: Optional[Dict[str, Any]] = Field(None, description="Notification payload")
    data: Optional[Dict[str, str]] = Field(None, description="Data payload")
    android: Optional[Dict[str, Any]] = Field(None, description="Android specific config")
    ios: Optional[Dict[str, Any]] = Field(None, description="iOS specific config")
    web: Optional[Dict[str, Any]] = Field(None, description="Web specific config")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eXQJ8V9K5fD:APA91bH...",
                "notification": {
                    "title": "Custom Title",
                    "body": "Custom Body",
                    "image": "https://example.com/image.png"
                },
                "data": {
                    "key1": "value1",
                    "key2": "value2"
                },
                "android": {
                    "priority": "high",
                    "notification": {
                        "icon": "stock_ticker_update",
                        "color": "#f45342"
                    }
                }
            }
        }


class TopicSubscriptionRequest(BaseModel):
    """Topic subscription request"""
    tokens: List[str] = Field(..., description="List of FCM device tokens")
    topic: str = Field(..., description="Topic name to subscribe/unsubscribe")

    class Config:
        json_schema_extra = {
            "example": {
                "tokens": ["token1", "token2", "token3"],
                "topic": "news"
            }
        }


class TokenValidationRequest(BaseModel):
    """Token validation request"""
    token: str = Field(..., description="FCM device token to validate")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eXQJ8V9K5fD:APA91bH..."
            }
        }


class FCMResponse(BaseModel):
    """FCM operation response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message_id: Optional[str] = Field(None, description="FCM message ID")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Notification sent successfully",
                "message_id": "0:1234567890123456%31bd1c9431bd1c94",
                "data": {
                    "multicast_id": 216,
                    "success": 1,
                    "failure": 0
                }
            }
        }


class TokenValidationResponse(BaseModel):
    """Token validation response"""
    token: str = Field(..., description="The validated token")
    is_valid: bool = Field(..., description="Token validity status")
    details: Optional[Dict[str, Any]] = Field(None, description="Validation details")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eXQJ8V9K5fD:APA91bH...",
                "is_valid": True,
                "details": {
                    "success": True,
                    "status_code": 200
                }
            }
        }
