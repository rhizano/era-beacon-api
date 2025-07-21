import requests
import json
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
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

    async def get_employees_exceeding_threshold(self, threshold: int) -> List[Dict[str, Any]]:
        """
        Query the v_presence_tracking view for employees exceeding the threshold.
        
        Args:
            threshold: Duration in minutes to check against
            
        Returns:
            List of dictionaries containing Employee ID and Employee Token
        """
        try:
            query = text("""
                SELECT "Employee ID", "Employee Token" 
                FROM v_presence_tracking vpt 
                WHERE duration_minutes >= :threshold
            """)
            
            print(f"DEBUG: Executing query with threshold: {threshold}")
            print(f"DEBUG: Query: {query}")
            logger.info(f"Executing query with threshold: {threshold}")
            logger.info(f"Query: {query}")
            
            # Test database connection and view existence first
            try:
                test_query = text("SELECT COUNT(*) FROM v_presence_tracking")
                test_result = self.db.execute(test_query)
                total_count = test_result.scalar()
                print(f"DEBUG: Total rows in v_presence_tracking view: {total_count}")
                logger.info(f"Total rows in v_presence_tracking view: {total_count}")
            except Exception as test_e:
                print(f"DEBUG: Failed to access v_presence_tracking view: {test_e}")
                logger.error(f"Failed to access v_presence_tracking view: {test_e}")
                raise
            
            result = self.db.execute(query, {"threshold": threshold})
            employees = []
            
            # Debug: Log raw result
            rows = result.fetchall()
            print(f"DEBUG: Raw query result: {len(rows)} rows returned")
            logger.info(f"Raw query result: {len(rows)} rows returned")
            
            for i, row in enumerate(rows):
                print(f"DEBUG: Row {i}: Employee ID='{row[0]}', Employee Token='{row[1]}'")
                logger.info(f"Row {i}: Employee ID='{row[0]}', Employee Token='{row[1]}'")
                employees.append({
                    "employee_id": row[0],  # Employee ID
                    "employee_token": row[1]  # Employee Token
                })
            
            print(f"DEBUG: Found {len(employees)} employees exceeding threshold of {threshold} minutes")
            logger.info(f"Found {len(employees)} employees exceeding threshold of {threshold} minutes")
            return employees
            
        except Exception as e:
            print(f"DEBUG: Error querying v_presence_tracking view: {str(e)}")
            print(f"DEBUG: Exception type: {type(e).__name__}")
            print(f"DEBUG: Exception details: {repr(e)}")
            logger.error(f"Error querying v_presence_tracking view: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {repr(e)}")
            raise

    async def send_absence_notification(self, employee_token: str, employee_id: str) -> bool:
        """
        Send FCM notification for absence to a specific employee.
        
        Args:
            employee_token: FCM token for the employee
            employee_id: Employee ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification_payload = {
                "token": employee_token,
                "title": "No Presence Detected!",
                "body": "Out of store range",
                "data": {
                    "employee_id": employee_id
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.notification_url,
                    json=notification_payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully sent absence notification to employee {employee_id}")
                    return True
                else:
                    logger.error(f"Failed to send absence notification to employee {employee_id}. Status: {response.status_code}, Response: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending absence notification to employee {employee_id}: {str(e)}")
            return False

    async def notify_absence(self, threshold: int) -> Dict[str, Any]:
        """
        Main method to handle absence notifications.
        
        Args:
            threshold: Duration threshold in minutes
            
        Returns:
            Dictionary with notification results
        """
        try:
            print(f"DEBUG: Starting notify_absence with threshold: {threshold}")
            logger.info(f"Starting notify_absence with threshold: {threshold}")
            
            # Get employees exceeding threshold
            employees = await self.get_employees_exceeding_threshold(threshold)
            
            print(f"DEBUG: notify_absence: Retrieved {len(employees)} employees")
            logger.info(f"notify_absence: Retrieved {len(employees)} employees")
            
            if not employees:
                print(f"DEBUG: No employees found exceeding threshold of {threshold} minutes")
                logger.warning(f"No employees found exceeding threshold of {threshold} minutes")
                return {
                    "success": True,
                    "message": f"No employees found exceeding threshold of {threshold} minutes",
                    "total_employees": 0,
                    "notifications_sent": 0,
                    "notifications_failed": 0
                }
            
            # Send notifications
            successful_notifications = 0
            failed_notifications = 0
            
            logger.info(f"Starting to send notifications to {len(employees)} employees")
            
            for employee in employees:
                success = await self.send_absence_notification(
                    employee["employee_token"], 
                    employee["employee_id"]
                )
                
                if success:
                    successful_notifications += 1
                else:
                    failed_notifications += 1
            
            result = {
                "success": True,
                "message": f"Processed {len(employees)} employees",
                "total_employees": len(employees),
                "notifications_sent": successful_notifications,
                "notifications_failed": failed_notifications,
                "threshold_minutes": threshold
            }
            
            logger.info(f"notify_absence completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in notify_absence: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {repr(e)}")
            return {
                "success": False,
                "message": f"Error processing absence notifications: {str(e)}",
                "total_employees": 0,
                "notifications_sent": 0,
                "notifications_failed": 0
            }
