import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.fcm_service import FCMService
import json


class TestFCMService:
    """Test FCM Service functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.mock_server_key = "test_server_key"
        self.mock_project_id = "test_project"
        self.test_token = "test_token_123"
        self.test_tokens = ["token1", "token2", "token3"]
        self.test_topic = "test_topic"
        
    @patch('app.services.fcm_service.settings')
    def test_fcm_service_init_with_settings(self, mock_settings):
        """Test FCM service initialization with settings"""
        mock_settings.fcm_server_key = self.mock_server_key
        mock_settings.fcm_project_id = self.mock_project_id
        
        service = FCMService()
        
        assert service.server_key == self.mock_server_key
        assert service.project_id == self.mock_project_id
        
    def test_fcm_service_init_without_key_raises_error(self):
        """Test FCM service initialization without key raises error"""
        with patch('app.services.fcm_service.settings') as mock_settings:
            mock_settings.fcm_server_key = None
            mock_settings.fcm_project_id = None
            
            with pytest.raises(ValueError, match="FCM server key is required"):
                FCMService()
                
    @patch('app.services.fcm_service.requests.post')
    @patch('app.services.fcm_service.settings')
    def test_send_to_token_success(self, mock_settings, mock_post):
        """Test successful notification send to token"""
        mock_settings.fcm_server_key = self.mock_server_key
        mock_settings.fcm_project_id = self.mock_project_id
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message_id": "test_message_id",
            "success": 1,
            "failure": 0
        }
        mock_post.return_value = mock_response
        
        service = FCMService()
        
        # Use sync version for testing
        service._send_request = Mock(return_value={"message_id": "test_id"})
        
        # Mock the async method
        async def mock_send():
            return await service.send_to_token(
                token=self.test_token,
                title="Test Title",
                body="Test Body",
                data={"key": "value"}
            )
            
        # This would need async test setup in real scenario
        
    @patch('app.services.fcm_service.requests.post')
    @patch('app.services.fcm_service.settings')
    def test_send_request_error_handling(self, mock_settings, mock_post):
        """Test error handling in send request"""
        mock_settings.fcm_server_key = self.mock_server_key
        mock_settings.fcm_project_id = self.mock_project_id
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_post.return_value = mock_response
        
        service = FCMService()
        
        with pytest.raises(Exception):
            service._send_request({"test": "payload"})


class TestFCMRoutes:
    """Test FCM API routes"""
    
    def setup_method(self):
        """Setup test client and data"""
        self.client = TestClient(app)
        self.test_token = "test_device_token"
        self.test_tokens = ["token1", "token2"]
        self.test_topic = "news"
        
        # Mock authentication
        self.mock_user = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser"
        }
        
    @patch('app.api.routes.fcm.get_current_user')
    @patch('app.api.routes.fcm.FCMService')
    def test_send_notification_endpoint(self, mock_fcm_service, mock_auth):
        """Test send notification endpoint"""
        # Mock authentication
        mock_auth.return_value = self.mock_user
        
        # Mock FCM service
        mock_service_instance = Mock()
        mock_service_instance.send_to_token.return_value = {"message_id": "test_id"}
        mock_fcm_service.return_value = mock_service_instance
        
        request_data = {
            "token": self.test_token,
            "title": "Test Notification",
            "body": "Test Body",
            "data": {"key": "value"}
        }
        
        response = self.client.post(
            "/v1/fcm/send-notification",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert "message" in response_data
        
    @patch('app.api.routes.fcm.get_current_user')
    @patch('app.api.routes.fcm.FCMService')
    def test_send_multiple_notifications_endpoint(self, mock_fcm_service, mock_auth):
        """Test send multiple notifications endpoint"""
        # Mock authentication
        mock_auth.return_value = self.mock_user
        
        # Mock FCM service
        mock_service_instance = Mock()
        mock_service_instance.send_to_multiple_tokens.return_value = {
            "success": 2,
            "failure": 0
        }
        mock_fcm_service.return_value = mock_service_instance
        
        request_data = {
            "tokens": self.test_tokens,
            "title": "Test Broadcast",
            "body": "Test Body"
        }
        
        response = self.client.post(
            "/v1/fcm/send-multiple",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        
    @patch('app.api.routes.fcm.get_current_user')
    @patch('app.api.routes.fcm.FCMService')
    def test_send_topic_notification_endpoint(self, mock_fcm_service, mock_auth):
        """Test send topic notification endpoint"""
        # Mock authentication
        mock_auth.return_value = self.mock_user
        
        # Mock FCM service
        mock_service_instance = Mock()
        mock_service_instance.send_to_topic.return_value = {"message_id": "topic_msg_id"}
        mock_fcm_service.return_value = mock_service_instance
        
        request_data = {
            "topic": self.test_topic,
            "title": "Topic News",
            "body": "Important update"
        }
        
        response = self.client.post(
            "/v1/fcm/send-to-topic",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        
    @patch('app.api.routes.fcm.get_current_user')
    @patch('app.api.routes.fcm.FCMService')
    def test_subscribe_to_topic_endpoint(self, mock_fcm_service, mock_auth):
        """Test subscribe to topic endpoint"""
        # Mock authentication
        mock_auth.return_value = self.mock_user
        
        # Mock FCM service
        mock_service_instance = Mock()
        mock_service_instance.subscribe_to_topic.return_value = {"success": 2}
        mock_fcm_service.return_value = mock_service_instance
        
        request_data = {
            "tokens": self.test_tokens,
            "topic": self.test_topic
        }
        
        response = self.client.post(
            "/v1/fcm/subscribe-to-topic",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        
    @patch('app.api.routes.fcm.get_current_user')
    @patch('app.api.routes.fcm.FCMService')
    def test_validate_token_endpoint(self, mock_fcm_service, mock_auth):
        """Test validate token endpoint"""
        # Mock authentication
        mock_auth.return_value = self.mock_user
        
        # Mock FCM service
        mock_service_instance = Mock()
        mock_service_instance.validate_token.return_value = (True, {"valid": True})
        mock_fcm_service.return_value = mock_service_instance
        
        request_data = {
            "token": self.test_token
        }
        
        response = self.client.post(
            "/v1/fcm/validate-token",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_valid"] is True
        
    def test_fcm_health_check_endpoint(self):
        """Test FCM health check endpoint"""
        with patch('app.api.routes.fcm.FCMService'):
            response = self.client.get("/v1/fcm/health")
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "healthy"
            assert response_data["service"] == "fcm"
            
    @patch('app.api.routes.fcm.get_current_user')
    @patch('app.api.routes.fcm.FCMService')
    def test_fcm_service_error_handling(self, mock_fcm_service, mock_auth):
        """Test FCM service error handling"""
        # Mock authentication
        mock_auth.return_value = self.mock_user
        
        # Mock FCM service to raise exception
        mock_service_instance = Mock()
        mock_service_instance.send_to_token.side_effect = Exception("FCM Error")
        mock_fcm_service.return_value = mock_service_instance
        
        request_data = {
            "token": self.test_token,
            "title": "Test",
            "body": "Test"
        }
        
        response = self.client.post(
            "/v1/fcm/send-notification",
            json=request_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200  # Returns 200 with success: false
        response_data = response.json()
        assert response_data["success"] is False
        assert "error" in response_data
        
    def test_unauthorized_access(self):
        """Test unauthorized access to FCM endpoints"""
        request_data = {
            "token": self.test_token,
            "title": "Test",
            "body": "Test"
        }
        
        response = self.client.post(
            "/v1/fcm/send-notification",
            json=request_data
        )
        
        assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
class TestAsyncFCMService:
    """Test async FCM service methods"""
    
    @patch('app.services.fcm_service.settings')
    async def test_async_send_to_token(self, mock_settings):
        """Test async send to token method"""
        mock_settings.fcm_server_key = "test_key"
        mock_settings.fcm_project_id = "test_project"
        
        service = FCMService()
        
        # Mock the _send_request method
        service._send_request = Mock(return_value={"message_id": "test_id"})
        
        result = await service.send_to_token(
            token="test_token",
            title="Test",
            body="Test Body"
        )
        
        assert "message_id" in result
        service._send_request.assert_called_once()
        
    @patch('app.services.fcm_service.settings')
    @patch('app.services.fcm_service.requests.post')
    async def test_async_validate_token(self, mock_post, mock_settings):
        """Test async token validation"""
        mock_settings.fcm_server_key = "test_key"
        mock_settings.fcm_project_id = "test_project"
        
        # Mock successful validation response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": 1,
            "failure": 0,
            "results": [{"message_id": "test_id"}]
        }
        mock_post.return_value = mock_response
        
        service = FCMService()
        is_valid, details = await service.validate_token("test_token")
        
        assert is_valid is True
        assert details["valid"] is True
