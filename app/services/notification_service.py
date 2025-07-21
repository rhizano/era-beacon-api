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
            # The view's duration_minutes is calculated incorrectly due to timezone issues
            # Let's create our own calculation that properly handles:
            # 1. Employees with no presence logs (Last Detection = shift start time)  
            # 2. Employees with actual presence logs but haven't been seen for a while
            query = text("""
                SELECT "Employee ID", "Employee Token",
                       CASE 
                           WHEN "Last Detection" = (CURRENT_DATE || ' ' || "Shift In")::timestamp THEN 
                               -- No actual presence logs, use full shift duration
                               EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - (CURRENT_DATE || ' ' || "Shift In")::timestamp) / 60
                           ELSE 
                               -- Has presence logs, calculate time since last detection
                               EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - "Last Detection") / 60
                       END as calculated_minutes
                FROM v_presence_tracking vpt 
                WHERE (
                    -- Employee with no presence logs (Last Detection = shift start)
                    "Last Detection" = (CURRENT_DATE || ' ' || "Shift In")::timestamp
                    AND EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - (CURRENT_DATE || ' ' || "Shift In")::timestamp) / 60 >= :threshold
                ) OR (
                    -- Employee with presence logs but absent for threshold time
                    "Last Detection" > (CURRENT_DATE || ' ' || "Shift In")::timestamp
                    AND EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - "Last Detection") / 60 >= :threshold
                )
            """)
            
            print(f"DEBUG: Executing query with threshold: {threshold}")
            print(f"DEBUG: Query: {query}")
            logger.info(f"Executing query with threshold: {threshold}")
            logger.info(f"Query: {query}")
            
            # Test database connection and view existence first
            try:
                # Check database connection details
                db_url_query = text("SELECT current_database(), current_user, inet_server_addr(), inet_server_port()")
                db_info = self.db.execute(db_url_query).fetchone()
                print(f"DEBUG: Database info - DB: {db_info[0]}, User: {db_info[1]}, Host: {db_info[2]}, Port: {db_info[3]}")
                
                # Check current timezone settings
                import datetime
                import time
                print(f"DEBUG: Python local time: {datetime.datetime.now()}")
                print(f"DEBUG: Python UTC time: {datetime.datetime.now(datetime.timezone.utc)}")
                print(f"DEBUG: System timezone: {time.tzname}")
                
                # Check database timezone and set it correctly
                db_time_query = text("SELECT now(), current_setting('timezone')")
                db_time_info = self.db.execute(db_time_query).fetchone()
                print(f"DEBUG: Database time: {db_time_info[0]}, Database timezone: {db_time_info[1]}")
                
                # Set database session timezone to match server
                set_tz_query = text("SET timezone = 'Asia/Jakarta'")
                self.db.execute(set_tz_query)
                self.db.commit()
                
                # Check timezone after setting
                db_time_query2 = text("SELECT now(), current_setting('timezone')")
                db_time_info2 = self.db.execute(db_time_query2).fetchone()
                print(f"DEBUG: Database time after timezone set: {db_time_info2[0]}, Database timezone: {db_time_info2[1]}")
                
                test_query = text("SELECT COUNT(*) FROM v_presence_tracking")
                test_result = self.db.execute(test_query)
                total_count = test_result.scalar()
                print(f"DEBUG: Total rows in v_presence_tracking view: {total_count}")
                logger.info(f"Total rows in v_presence_tracking view: {total_count}")
                
                # Check the actual column names and data
                inspect_query = text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'v_presence_tracking'
                    ORDER BY ordinal_position
                """)
                columns_result = self.db.execute(inspect_query)
                columns = columns_result.fetchall()
                print(f"DEBUG: View columns: {[(col[0], col[1]) for col in columns]}")
                
                # Check actual data in the view - show ALL rows since there are only 2
                sample_query = text("SELECT * FROM v_presence_tracking ORDER BY duration_minutes DESC")
                sample_result = self.db.execute(sample_query)
                sample_rows = sample_result.fetchall()
                print(f"DEBUG: ALL data from view (ordered by duration_minutes DESC):")
                for i, row in enumerate(sample_rows):
                    print(f"DEBUG: Row {i}: {dict(row._mapping)}")
                
                # Test the exact query with different thresholds
                for test_threshold in [30, 0, -1000]:
                    test_query = text("SELECT COUNT(*) FROM v_presence_tracking WHERE duration_minutes >= :threshold")
                    test_result = self.db.execute(test_query, {"threshold": test_threshold})
                    test_count = test_result.scalar()
                    print(f"DEBUG: Rows with duration_minutes >= {test_threshold}: {test_count}")
                    
                # Test the new corrected query logic
                test_query = text("""
                    SELECT "Employee ID", "Employee Token", "Last Detection", "Shift In",
                           (CURRENT_DATE || ' ' || "Shift In")::timestamp as shift_start_today,
                           CASE 
                               WHEN "Last Detection" = (CURRENT_DATE || ' ' || "Shift In")::timestamp THEN 'NO_PRESENCE_LOGS'
                               ELSE 'HAS_PRESENCE_LOGS'
                           END as presence_status,
                           CASE 
                               WHEN "Last Detection" = (CURRENT_DATE || ' ' || "Shift In")::timestamp THEN 
                                   EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - (CURRENT_DATE || ' ' || "Shift In")::timestamp) / 60
                               ELSE 
                                   EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - "Last Detection") / 60
                           END as calculated_minutes
                    FROM v_presence_tracking 
                    ORDER BY "Employee ID"
                """)
                test_result = self.db.execute(test_query)
                test_rows = test_result.fetchall()
                print(f"DEBUG: Corrected absence calculation for ALL employees:")
                for i, row in enumerate(test_rows):
                    print(f"DEBUG: Employee {i}: ID='{row[0]}', Last Detection='{row[2]}', Shift Start Today='{row[4]}', Status='{row[5]}', Minutes='{row[6]}'")
                
                # Test with different thresholds using new logic
                for test_threshold in [30, 0]:
                    threshold_query = text("""
                        SELECT "Employee ID", "Employee Token",
                               CASE 
                                   WHEN "Last Detection" = (CURRENT_DATE || ' ' || "Shift In")::timestamp THEN 
                                       EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - (CURRENT_DATE || ' ' || "Shift In")::timestamp) / 60
                                   ELSE 
                                       EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - "Last Detection") / 60
                               END as calculated_minutes
                        FROM v_presence_tracking vpt 
                        WHERE (
                            "Last Detection" = (CURRENT_DATE || ' ' || "Shift In")::timestamp
                            AND EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - (CURRENT_DATE || ' ' || "Shift In")::timestamp) / 60 >= :threshold
                        ) OR (
                            "Last Detection" > (CURRENT_DATE || ' ' || "Shift In")::timestamp
                            AND EXTRACT(epoch FROM (now() AT TIME ZONE 'Asia/Jakarta') - "Last Detection") / 60 >= :threshold
                        )
                    """)
                    threshold_result = self.db.execute(threshold_query, {"threshold": test_threshold})
                    threshold_rows = threshold_result.fetchall()
                    print(f"DEBUG: New query with threshold {test_threshold}: {len(threshold_rows)} employees")
                    for i, row in enumerate(threshold_rows):
                        print(f"DEBUG: Threshold {test_threshold} - Employee {i}: ID='{row[0]}', Minutes='{row[2]}'")
                
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
                print(f"DEBUG: Row {i}: Employee ID='{row[0]}', Employee Token='{row[1]}', Calculated Minutes='{row[2]}'")
                logger.info(f"Row {i}: Employee ID='{row[0]}', Employee Token='{row[1]}', Calculated Minutes='{row[2]}'")
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

    async def send_absence_notification(self, employee_token: str, employee_id: str) -> Dict[str, Any]:
        """
        Send FCM notification for absence to a specific employee.
        
        Args:
            employee_token: FCM token for the employee
            employee_id: Employee ID
            
        Returns:
            Dictionary with detailed notification result including curl and response info
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
            
            # Generate curl command for debugging
            curl_command = f"curl -X POST '{self.notification_url}' \\\n"
            curl_command += f"  -H 'Content-Type: application/json' \\\n"
            curl_command += f"  -d '{json.dumps(notification_payload)}'"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.notification_url,
                    json=notification_payload,
                    headers=headers,
                    timeout=30.0
                )
                
                result = {
                    "employee_id": employee_id,
                    "request_curl": curl_command,
                    "response_code": response.status_code,
                    "response_message": response.text if response.text else "No response body"
                }
                
                if response.status_code == 200:
                    logger.info(f"Successfully sent absence notification to employee {employee_id}")
                    result["success"] = True
                else:
                    logger.error(f"Failed to send absence notification to employee {employee_id}. Status: {response.status_code}, Response: {response.text}")
                    result["success"] = False
                
                return result
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error sending absence notification to employee {employee_id}: {error_msg}")
            
            # Generate curl command even for failed requests
            curl_command = f"curl -X POST '{self.notification_url}' \\\n"
            curl_command += f"  -H 'Content-Type: application/json' \\\n"
            curl_command += f"  -d '{json.dumps(notification_payload) if 'notification_payload' in locals() else '{}'}'"
            
            return {
                "employee_id": employee_id,
                "request_curl": curl_command,
                "response_code": 0,
                "response_message": f"Request failed: {error_msg}",
                "success": False
            }

    async def notify_absence(self, threshold: int) -> Dict[str, Any]:
        """
        Main method to handle absence notifications.
        
        Args:
            threshold: Duration threshold in minutes
            
        Returns:
            Dictionary with detailed notification results including curl requests and responses
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
                    "threshold_minutes": threshold,
                    "message": f"No employees found exceeding threshold of {threshold} minutes",
                    "total_employees": 0,
                    "notifications_sent": 0,
                    "notifications_failed": 0,
                    "notifications_detail": []
                }
            
            # Send notifications and collect detailed results
            successful_notifications = 0
            failed_notifications = 0
            notifications_detail = []
            
            logger.info(f"Starting to send notifications to {len(employees)} employees")
            
            for employee in employees:
                notification_result = await self.send_absence_notification(
                    employee["employee_token"], 
                    employee["employee_id"]
                )
                
                # Add to details list
                notifications_detail.append({
                    "employee_id": notification_result["employee_id"],
                    "request_curl": notification_result["request_curl"],
                    "response_code": notification_result["response_code"],
                    "response_message": notification_result["response_message"]
                })
                
                if notification_result["success"]:
                    successful_notifications += 1
                else:
                    failed_notifications += 1
            
            result = {
                "success": True,
                "threshold_minutes": threshold,
                "message": f"Processed {len(employees)} employees",
                "total_employees": len(employees),
                "notifications_sent": successful_notifications,
                "notifications_failed": failed_notifications,
                "notifications_detail": notifications_detail
            }
            
            logger.info(f"notify_absence completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in notify_absence: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {repr(e)}")
            return {
                "success": False,
                "threshold_minutes": threshold,
                "message": f"Error processing absence notifications: {str(e)}",
                "total_employees": 0,
                "notifications_sent": 0,
                "notifications_failed": 0,
                "notifications_detail": []
            }
