import json
import requests
import os
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from fastapi import HTTPException, status
import logging
from app.core.config import settings
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.auth

logger = logging.getLogger(__name__)


class FCMMessage(BaseModel):
    """FCM message structure"""
    token: Optional[str] = None
    topic: Optional[str] = None
    condition: Optional[str] = None
    notification: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, str]] = None
    android: Optional[Dict[str, Any]] = None
    ios: Optional[Dict[str, Any]] = None
    web: Optional[Dict[str, Any]] = None


class FCMNotification(BaseModel):
    """FCM notification structure"""
    title: str
    body: str
    image: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tag: Optional[str] = None
    click_action: Optional[str] = None


class FCMAndroidConfig(BaseModel):
    """FCM Android specific configuration"""
    collapse_key: Optional[str] = None
    priority: Optional[str] = None  # "normal" or "high"
    ttl: Optional[str] = None
    restricted_package_name: Optional[str] = None
    data: Optional[Dict[str, str]] = None
    notification: Optional[Dict[str, Any]] = None


class FCMWebConfig(BaseModel):
    """FCM Web specific configuration"""
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, str]] = None
    notification: Optional[Dict[str, Any]] = None


class FCMService:
    """Firebase Cloud Messaging service using Service Account authentication"""
    
    def __init__(self, service_account_path: str = None, project_id: str = None):
        self.service_account_path = service_account_path or settings.fcm_service_account_key_path
        self.project_id = project_id or settings.fcm_project_id
        
        # Set default values from the service account file if provided
        if self.service_account_path and os.path.exists(self.service_account_path):
            with open(self.service_account_path, 'r') as f:
                service_account_info = json.load(f)
                if not self.project_id:
                    self.project_id = service_account_info.get('project_id')
        elif self.service_account_path and not os.path.exists(self.service_account_path):
            logger.warning(f"Service account file not found: {self.service_account_path}")
        
        if not self.project_id:
            raise ValueError("FCM project ID is required. Set FCM_PROJECT_ID environment variable or provide service account key.")
            
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        self.fcm_v1_url = f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send"
        self.scopes = ['https://www.googleapis.com/auth/firebase.messaging']
        
        # Initialize credentials
        self._credentials = None
        self._access_token = None
        
    def _get_access_token(self) -> str:
        """Get access token for FCM API v1"""
        try:
            if self.service_account_path and os.path.exists(self.service_account_path):
                # Use service account for authentication
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_path, 
                    scopes=self.scopes
                )
                credentials.refresh(Request())
                logger.info(f"Successfully obtained access token for project: {self.project_id}")
                return credentials.token
            else:
                # Fallback to default credentials (for Cloud environments)
                try:
                    credentials, project = google.auth.default(scopes=self.scopes)
                    credentials.refresh(Request())
                    logger.info(f"Successfully obtained default credentials for project: {project}")
                    return credentials.token
                except Exception as e:
                    logger.error(f"Failed to get default credentials: {str(e)}")
                    # If no service account and no default credentials, we'll need a server key
                    server_key = settings.fcm_server_key
                    if server_key:
                        logger.warning("Using legacy server key authentication")
                        return server_key
                    else:
                        raise ValueError("No valid authentication method found. Provide service account key or server key.")
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise
    
    def _get_headers_v1(self) -> Dict[str, str]:
        """Get headers for FCM API v1"""
        access_token = self._get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _get_headers_legacy(self) -> Dict[str, str]:
        """Get headers for legacy FCM API"""
        server_key = settings.fcm_server_key or self._get_access_token()
        return {
            "Authorization": f"key={server_key}",
            "Content-Type": "application/json"
        }
    
    def check_service_account_permissions(self) -> Dict[str, Any]:
        """Check if the service account has proper FCM permissions"""
        try:
            access_token = self._get_access_token()
            logger.info(f"Successfully obtained access token")
            
            # Try to validate a dummy token to check permissions
            test_message = {
                "message": {
                    "token": "dummy_token_for_testing",
                    "notification": {
                        "title": "Test",
                        "body": "Permission test"
                    }
                },
                "validate_only": True
            }
            
            headers = self._get_headers_v1()
            response = requests.post(self.fcm_v1_url, json=test_message, headers=headers, timeout=10)
            
            logger.info(f"Permission test response: {response.status_code}")
            if response.status_code == 403:
                error_detail = response.json() if response.text else "No error details"
                logger.error(f"403 Permission error details: {error_detail}")
                return {
                    "has_permissions": False,
                    "error": "Service account lacks FCM permissions",
                    "details": error_detail,
                    "status_code": 403
                }
            else:
                return {
                    "has_permissions": True,
                    "message": "Service account has proper FCM permissions",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error checking permissions: {str(e)}")
            return {
                "has_permissions": False,
                "error": str(e),
                "details": "Failed to check permissions"
            }
        
    async def send_to_token(self, 
                           token: str, 
                           title: str, 
                           body: str, 
                           data: Optional[Dict[str, str]] = None,
                           image: Optional[str] = None,
                           click_action: Optional[str] = None,
                           link: Optional[str] = None) -> Dict[str, Any]:
        """Send notification to a specific device token using FCM v1 API"""
        
        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }
        
        if image:
            message["message"]["notification"]["image"] = image
            
        if data or link:
            message_data = data.copy() if data else {}
            if link:
                message_data["link"] = link
            if click_action:
                message_data["click_action"] = click_action
            message["message"]["data"] = message_data
            
        return self._send_request_v1(message)
    
    async def send_to_multiple_tokens(self,
                                    tokens: List[str],
                                    title: str,
                                    body: str,
                                    data: Optional[Dict[str, str]] = None,
                                    image: Optional[str] = None,
                                    click_action: Optional[str] = None,
                                    link: Optional[str] = None) -> Dict[str, Any]:
        """Send notification to multiple device tokens using FCM v1 API"""
        
        # FCM v1 API requires individual requests for multiple tokens
        results = []
        success_count = 0
        failure_count = 0
        
        for token in tokens:
            try:
                result = await self.send_to_token(
                    token=token,
                    title=title,
                    body=body,
                    data=data,
                    image=image,
                    click_action=click_action,
                    link=link
                )
                results.append({"token": token, "success": True, "result": result})
                success_count += 1
            except Exception as e:
                results.append({"token": token, "success": False, "error": str(e)})
                failure_count += 1
                
        return {
            "multicast_id": "bulk_" + str(hash(tuple(tokens))),
            "success": success_count,
            "failure": failure_count,
            "canonical_ids": 0,
            "results": results
        }
    
    async def send_to_topic(self,
                          topic: str,
                          title: str,
                          body: str,
                          data: Optional[Dict[str, str]] = None,
                          image: Optional[str] = None,
                          click_action: Optional[str] = None) -> Dict[str, Any]:
        """Send notification to a topic using FCM v1 API"""
        
        message = {
            "message": {
                "topic": topic,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }
        
        if image:
            message["message"]["notification"]["image"] = image
            
        if data or click_action:
            message_data = data.copy() if data else {}
            if click_action:
                message_data["click_action"] = click_action
            message["message"]["data"] = message_data
            
        return self._send_request_v1(message)
    
    async def send_custom_message(self,
                                token: Optional[str] = None,
                                topic: Optional[str] = None,
                                condition: Optional[str] = None,
                                notification: Optional[Dict[str, Any]] = None,
                                data: Optional[Dict[str, str]] = None,
                                android: Optional[Dict[str, Any]] = None,
                                ios: Optional[Dict[str, Any]] = None,
                                web: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send custom FCM message with full control over payload using FCM v1 API"""
        
        if not any([token, topic, condition]):
            raise ValueError("At least one of token, topic, or condition must be provided")
        
        message = {"message": {}}
        
        if token:
            message["message"]["token"] = token
        elif topic:
            message["message"]["topic"] = topic
        elif condition:
            message["message"]["condition"] = condition
            
        if notification:
            message["message"]["notification"] = notification
            
        if data:
            message["message"]["data"] = data
            
        if android:
            message["message"]["android"] = android
            
        if ios:
            message["message"]["apns"] = ios
            
        if web:
            message["message"]["webpush"] = web
            
        return self._send_request_v1(message)
    
    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Subscribe device tokens to a topic"""
        
        url = f"https://iid.googleapis.com/iid/v1:batchAdd"
        payload = {
            "to": f"/topics/{topic}",
            "registration_tokens": tokens
        }
        
        headers = self._get_headers_legacy()
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully subscribed {len(tokens)} tokens to topic '{topic}'")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error subscribing to topic: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to subscribe to topic: {str(e)}"
            )
    
    async def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Unsubscribe device tokens from a topic"""
        
        url = f"https://iid.googleapis.com/iid/v1:batchRemove"
        payload = {
            "to": f"/topics/{topic}",
            "registration_tokens": tokens
        }
        
        headers = self._get_headers_legacy()
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully unsubscribed {len(tokens)} tokens from topic '{topic}'")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error unsubscribing from topic: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to unsubscribe from topic: {str(e)}"
            )
    
    async def validate_token(self, token: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate an FCM device token using FCM v1 API"""
        
        # Use a test message with validate_only flag
        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": "Validation",
                    "body": "This is a validation message"
                }
            },
            "validate_only": True
        }
        
        try:
            response = requests.post(
                self.fcm_v1_url, 
                json=message, 
                headers=self._get_headers_v1(), 
                timeout=10
            )
            
            if response.status_code == 200:
                return True, {"valid": True, "response": response.json()}
            else:
                error_data = response.json() if response.text else {}
                return False, {
                    "valid": False, 
                    "error": f"HTTP {response.status_code}",
                    "response": error_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validating token: {str(e)}")
            return False, {"valid": False, "error": str(e)}
    
    def _send_request_v1(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send FCM request using v1 API"""
        
        headers = self._get_headers_v1()
        
        try:
            response = requests.post(self.fcm_v1_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"FCM v1 request successful: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"FCM v1 request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"FCM error response: {error_detail}")
                except:
                    error_detail = e.response.text
                    logger.error(f"FCM error text: {error_detail}")
                    
                # Provide specific guidance for 403 errors
                if e.response.status_code == 403:
                    logger.error("403 Forbidden: Check Firebase service account permissions")
                    
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"FCM error: {error_detail}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"FCM request failed: {str(e)}"
                )
