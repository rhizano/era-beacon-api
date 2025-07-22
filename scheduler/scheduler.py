"""
Era Beacon API Notification Scheduler

This module implements a job scheduler using APScheduler to automatically send
absence notifications during business hours on weekdays.

Features:
- Automatic authentication with the Era Beacon API
- Scheduled notifications every M minutes during business hours
- Weekday-only execution (Monday-Friday, 9:00-18:00)
- Configurable thresholds and intervals
- Comprehensive error handling and logging
- Token refresh on authentication failures

Dependencies:
- apscheduler>=3.10.0
- requests>=2.28.0
- configparser (built-in)

Usage:
    python scheduler.py

Configuration:
    Edit config.ini to customize the scheduler behavior.
"""

import configparser
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


class EraBeaconScheduler:
    """
    Job scheduler for Era Beacon API absence notifications.
    
    Handles authentication, scheduling, and notification sending with
    proper error handling and logging.
    """
    
    def __init__(self, config_file: str = "config.ini"):
        """
        Initialize the scheduler with configuration.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config = self._load_config(config_file)
        self.scheduler = BlockingScheduler()
        self.logger = self._setup_logging()
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # API endpoints
        self.base_url = self.config.get('scheduler', 'api_base_url')
        self.auth_url = f"{self.base_url}/auth/login"
        self.notify_url = f"{self.base_url}/notifications/notify-absence"
        
        # Authentication credentials
        self.username = self.config.get('scheduler', 'auth_username')
        self.password = self.config.get('scheduler', 'auth_password')
        
        # Scheduler configuration
        self.threshold_minutes = self.config.getint('scheduler', 'threshold_minutes')
        self.start_hour = self.config.getint('scheduler', 'weekday_start_hour')
        self.end_hour = self.config.getint('scheduler', 'weekday_end_hour')
        
        # Setup scheduler event listeners
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
    def _load_config(self, config_file: str) -> configparser.ConfigParser:
        """Load configuration from INI file."""
        # Use RawConfigParser to avoid interpolation issues with logging format
        config = configparser.RawConfigParser()
        try:
            config.read(config_file)
            return config
        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
            raise
            
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        
        # Get logging configuration
        log_level = self.config.get('logging', 'level', fallback='INFO')
        log_format = self.config.get('logging', 'format', 
                                   fallback='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = self.config.get('logging', 'file', fallback='scheduler.log')
        
        # Configure logging with multiple handlers
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatters
        formatter = logging.Formatter(log_format)
        
        # File handler for scheduler-specific logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        
        # Console handler for immediate output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        
        # Add server log integration (write to server's main log file if accessible)
        try:
            # Try to write to the main application log (common locations)
            server_log_paths = [
                '../app.log',  # Common FastAPI log location
                '../logs/app.log',
                '../application.log',
                '/var/log/era-beacon-api.log',  # Production log location
                'server.log'  # Fallback in current directory
            ]
            
            server_log_file = None
            for path in server_log_paths:
                try:
                    # Test if we can write to this location
                    with open(path, 'a') as test_file:
                        server_log_file = path
                        break
                except (IOError, OSError, PermissionError):
                    continue
            
            if server_log_file:
                server_handler = logging.FileHandler(server_log_file)
                server_handler.setLevel(logging.INFO)  # Always log important events to server
                server_formatter = logging.Formatter(
                    '%(asctime)s - SCHEDULER - %(levelname)s - %(message)s'
                )
                server_handler.setFormatter(server_formatter)
                logger.addHandler(server_handler)
                self.server_log_file = server_log_file
            else:
                self.server_log_file = None
                
        except Exception as e:
            self.server_log_file = None
            # Don't fail if server log integration doesn't work
            pass
        
        # Add all handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def _log_to_server(self, message: str, level: str = 'INFO'):
        """
        Log important events to the server's main log file.
        
        Args:
            message: The message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        try:
            if hasattr(self, 'server_log_file') and self.server_log_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"{timestamp} - SCHEDULER - {level} - {message}\n"
                
                with open(self.server_log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    f.flush()
        except Exception:
            # Don't fail if server logging doesn't work
            pass
            
    def _job_listener(self, event):
        """Listen to job execution events for logging."""
        if event.exception:
            error_msg = f"Scheduled job {event.job_id} crashed: {event.exception}"
            self.logger.error(error_msg)
            self._log_to_server(error_msg, 'ERROR')
        else:
            success_msg = f"Scheduled job {event.job_id} executed successfully"
            self.logger.info(success_msg)
            self._log_to_server(success_msg, 'INFO')
            
    def _is_business_hours(self) -> bool:
        """
        Check if current time is within business hours (weekdays 9:00-18:00).
        
        Returns:
            True if it's currently business hours, False otherwise
        """
        now = datetime.now()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
            
        # Check if it's within business hours
        current_hour = now.hour
        return self.start_hour <= current_hour < self.end_hour
        
    def authenticate(self) -> bool:
        """
        Authenticate with the Era Beacon API and obtain access token.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            auth_msg = "Attempting to authenticate with Era Beacon API"
            self.logger.info(auth_msg)
            self._log_to_server(auth_msg)
            
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.auth_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.access_token = auth_data.get("access_token")
                
                # Set token expiration (assume 1 hour if not provided)
                expires_in = auth_data.get("expires_in", 3600)  # Default 1 hour
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                success_msg = f"Authentication successful - Token expires at {self.token_expires_at}"
                self.logger.info(success_msg)
                self._log_to_server(success_msg)
                return True
            else:
                error_msg = f"Authentication failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                self._log_to_server(error_msg, 'ERROR')
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Authentication request failed: {e}"
            self.logger.error(error_msg)
            self._log_to_server(error_msg, 'ERROR')
            return False
        except Exception as e:
            error_msg = f"Unexpected error during authentication: {e}"
            self.logger.error(error_msg)
            self._log_to_server(error_msg, 'ERROR')
            return False
            
    def _is_token_valid(self) -> bool:
        """
        Check if the current access token is valid and not expired.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.access_token:
            return False
            
        if not self.token_expires_at:
            return False
            
        # Check if token expires within the next 5 minutes (buffer time)
        return datetime.now() < (self.token_expires_at - timedelta(minutes=5))
        
    def send_absence_notification(self) -> Dict[str, Any]:
        """
        Send absence notification request to the Era Beacon API.
        
        Returns:
            Dictionary containing the API response and status information
        """
        # Check if it's business hours
        if not self._is_business_hours():
            skip_msg = "Outside business hours, skipping notification"
            self.logger.info(skip_msg)
            self._log_to_server(skip_msg)
            return {
                "success": False,
                "message": "Outside business hours",
                "skipped": True
            }
            
        # Ensure we have a valid token
        if not self._is_token_valid():
            reauth_msg = "Token invalid or expired, attempting to re-authenticate"
            self.logger.info(reauth_msg)
            self._log_to_server(reauth_msg)
            if not self.authenticate():
                return {
                    "success": False,
                    "message": "Authentication failed",
                    "error": "Could not obtain valid access token"
                }
                
        try:
            notify_msg = f"Sending absence notification with threshold: {self.threshold_minutes} minutes"
            self.logger.info(notify_msg)
            self._log_to_server(notify_msg)
            
            payload = {
                "threshold": self.threshold_minutes
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.notify_url,
                json=payload,
                headers=headers,
                timeout=60  # Longer timeout for notification processing
            )
            
            if response.status_code == 200:
                response_data = response.json()
                success_msg = f"Notification sent successfully: {response_data.get('message', 'No message')}"
                self.logger.info(success_msg)
                self._log_to_server(success_msg)
                
                # Log notification details
                total_employees = response_data.get('total_employees', 0)
                notifications_sent = response_data.get('notifications_sent', 0)
                notifications_failed = response_data.get('notifications_failed', 0)
                
                summary_msg = f"Notification summary: {total_employees} employees processed, {notifications_sent} sent, {notifications_failed} failed"
                self.logger.info(summary_msg)
                self._log_to_server(summary_msg)
                
                # Log detailed results if available
                notifications_detail = response_data.get('notifications_detail', [])
                if notifications_detail:
                    for detail in notifications_detail:
                        employee_id = detail.get('employee_id', 'Unknown')
                        response_code = detail.get('response_code', 'Unknown')
                        response_msg = detail.get('response_message', 'No message')
                        
                        detail_msg = f"Employee {employee_id}: HTTP {response_code} - {response_msg[:100]}{'...' if len(response_msg) > 100 else ''}"
                        self.logger.debug(detail_msg)
                        
                        # Only log failed notifications to server log to avoid spam
                        if response_code != 200:
                            self._log_to_server(f"NOTIFICATION FAILED - {detail_msg}", 'WARNING')
                
                return {
                    "success": True,
                    "message": "Notification sent successfully",
                    "data": response_data
                }
            else:
                error_msg = f"Notification request failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                self._log_to_server(error_msg, 'ERROR')
                
                # If unauthorized, clear token to force re-authentication
                if response.status_code == 401:
                    unauth_msg = "Received 401 Unauthorized, clearing access token"
                    self.logger.info(unauth_msg)
                    self._log_to_server(unauth_msg, 'WARNING')
                    self.access_token = None
                    self.token_expires_at = None
                    
                return {
                    "success": False,
                    "message": f"API request failed with status {response.status_code}",
                    "error": response.text
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Notification request failed: {e}")
            return {
                "success": False,
                "message": "Network request failed",
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error during notification: {e}")
            return {
                "success": False,
                "message": "Unexpected error occurred",
                "error": str(e)
            }
            
    def scheduled_job(self):
        """
        The main scheduled job function.
        
        This function is called by the scheduler at regular intervals.
        """
        self.logger.info("Executing scheduled absence notification job")
        
        try:
            result = self.send_absence_notification()
            
            if result.get("success"):
                self.logger.info("Scheduled job completed successfully")
            elif result.get("skipped"):
                self.logger.debug("Scheduled job skipped (outside business hours)")
            else:
                self.logger.warning(f"Scheduled job failed: {result.get('message')}")
                
        except Exception as e:
            self.logger.error(f"Unexpected error in scheduled job: {e}")
            
    def start(self):
        """
        Start the scheduler with the configured job.
        
        The job will run every threshold_minutes during business hours.
        """
        try:
            self.logger.info("Starting Era Beacon Notification Scheduler")
            self.logger.info(f"Configuration: Threshold={self.threshold_minutes} minutes, "
                           f"Business hours: {self.start_hour}:00-{self.end_hour}:00 weekdays")
            
            # Initial authentication
            if not self.authenticate():
                self.logger.error("Initial authentication failed, scheduler may not work properly")
            
            # Add the scheduled job
            self.scheduler.add_job(
                func=self.scheduled_job,
                trigger=IntervalTrigger(minutes=self.threshold_minutes),
                id='absence_notification_job',
                name='Era Beacon Absence Notification',
                misfire_grace_time=300,  # 5 minutes grace time for missed jobs
                coalesce=True,  # Combine multiple missed jobs into one
                max_instances=1  # Only one instance of the job can run at a time
            )
            
            self.logger.info(f"Job scheduled to run every {self.threshold_minutes} minutes")
            self.logger.info("Scheduler started. Press Ctrl+C to stop.")
            
            # Start the scheduler (this will block)
            self.scheduler.start()
            
        except KeyboardInterrupt:
            self.logger.info("Scheduler interrupted by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
            raise
            
    def stop(self):
        """Stop the scheduler gracefully."""
        try:
            stop_msg = "Stopping scheduler..."
            self.logger.info(stop_msg)
            self._log_to_server(stop_msg, 'INFO')
            
            self.scheduler.shutdown(wait=True)
            
            success_msg = "Scheduler stopped successfully"
            self.logger.info(success_msg)
            self._log_to_server(success_msg, 'INFO')
        except Exception as e:
            error_msg = f"Error stopping scheduler: {e}"
            self.logger.error(error_msg)
            self._log_to_server(error_msg, 'ERROR')
            
    def run_once(self) -> Dict[str, Any]:
        """
        Run the notification job once (for testing purposes).
        
        Returns:
            Dictionary containing the result of the notification attempt
        """
        test_run_msg = "Running notification job once (test mode)"
        self.logger.info(test_run_msg)
        self._log_to_server(test_run_msg, 'INFO')
        
        try:
            return self.send_absence_notification()
        except Exception as e:
            error_msg = f"Error in test run: {e}"
            self.logger.error(error_msg)
            self._log_to_server(error_msg, 'ERROR')
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """Main entry point for the scheduler application."""
    scheduler = None
    try:
        # Create and start the scheduler
        scheduler = EraBeaconScheduler()
        
        # Log startup to both scheduler and server logs
        startup_msg = "Era Beacon API Scheduler application starting up"
        scheduler.logger.info(startup_msg)
        scheduler._log_to_server(startup_msg, 'INFO')
        
        scheduler.start()
        
        startup_success_msg = "Era Beacon API Scheduler started successfully - running in background"
        scheduler.logger.info(startup_success_msg)
        scheduler._log_to_server(startup_success_msg, 'INFO')
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            interrupt_msg = "Scheduler interrupted by user (Ctrl+C)"
            print("\nScheduler interrupted by user")
            scheduler.logger.info(interrupt_msg)
            scheduler._log_to_server(interrupt_msg, 'INFO')
        
    except KeyboardInterrupt:
        interrupt_msg = "Scheduler interrupted by user (Ctrl+C)"
        print("\nScheduler interrupted by user")
        if scheduler:
            scheduler.logger.info(interrupt_msg)
            scheduler._log_to_server(interrupt_msg, 'INFO')
    except Exception as e:
        error_msg = f"Fatal scheduler error: {e}"
        print(f"Error running scheduler: {e}")
        if scheduler:
            scheduler.logger.error(error_msg)
            scheduler._log_to_server(error_msg, 'ERROR')
        else:
            logging.error(error_msg)
    finally:
        if scheduler:
            scheduler.stop()


if __name__ == "__main__":
    main()
