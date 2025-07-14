import requests
import json
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.models.beacon import Beacon
from app.schemas.notification import NotifyToQleapRequest, NotifyToQleapResponse
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_url = "https://even-trainer-464609-d1.et.r.appspot.com/send-notification"

    def notify_to_qleap(self, request_data: NotifyToQleapRequest) -> NotifyToQleapResponse:
        """
        Send push notifications to all app_tokens associated with a beacon_id.
        """
        try:
            # Query the beacons table to get all app_tokens for the given beacon_id
            beacons = self.db.query(Beacon).filter(
                Beacon.beacon_id == request_data.beacon_id,
                Beacon.app_token.isnot(None),
                Beacon.app_token != ""
            ).all()

            if not beacons:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No beacons found with beacon_id '{request_data.beacon_id}' or no app_tokens available"
                )

            notifications_sent = 0
            failed_notifications = []

            # Send notification for each app_token
            for beacon in beacons:
                if beacon.app_token:
                    try:
                        success = self._send_push_notification(beacon.app_token)
                        if success:
                            notifications_sent += 1
                        else:
                            failed_notifications.append(beacon.app_token)
                    except Exception as e:
                        logger.error(f"Failed to send notification to token {beacon.app_token}: {str(e)}")
                        failed_notifications.append(beacon.app_token)

            if notifications_sent == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send any notifications"
                )

            message = f"Notifications sent successfully"
            if failed_notifications:
                message += f" ({len(failed_notifications)} failed)"

            return NotifyToQleapResponse(
                message=message,
                notifications_sent=notifications_sent,
                beacon_id=request_data.beacon_id
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in notify_to_qleap: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )

    def _send_push_notification(self, app_token: str) -> bool:
        """
        Send a push notification to a specific app_token.
        Returns True if successful, False otherwise.
        """
        payload = {
            "token": app_token,
            "title": "Eraspace Member is Detected!",
            "body": "Open Information",
            "link": "https://erabeacon-7e08e.web.app/"
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.notification_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=30  # 30 second timeout
            )
            
            # Log the response for debugging
            logger.info(f"Notification API response: {response.status_code} - {response.text}")
            
            # Consider success if status code is 2xx
            return 200 <= response.status_code < 300

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for token {app_token}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending notification to {app_token}: {str(e)}")
            return False
