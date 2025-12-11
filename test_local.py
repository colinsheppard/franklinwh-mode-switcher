import unittest
from unittest.mock import patch, MagicMock
import datetime
import pytz
import main
import config

class TestModeSwitcher(unittest.TestCase):

    @patch('main.get_secret')
    @patch('main.TokenFetcher')
    @patch('main.Client')
    def test_mode_switch_trigger(self, mock_client_cls, mock_fetcher_cls, mock_get_secret):
        # Mock secrets
        mock_get_secret.side_effect = lambda x, y=None: "dummy_value"
        
        # Mock Client instance
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.get_mode.return_value = "time_of_use" # Currently in TOU

        # Mock time to 00:05 (should trigger emergency_backup)
        tz = pytz.timezone(config.TIMEZONE)
        # 00:05
        mock_now = datetime.datetime(2023, 1, 1, 0, 5, 0, tzinfo=tz)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = datetime.datetime

            # Call the function
            request = MagicMock()
            response = main.mode_switcher(request)
            
            # Verify
            self.assertEqual(response, ("Switched to emergency_backup", 200))
            mock_client.set_mode.assert_called_with("emergency_backup")

    @patch('main.get_secret')
    @patch('main.TokenFetcher')
    @patch('main.Client')
    def test_no_action_needed(self, mock_client_cls, mock_fetcher_cls, mock_get_secret):
        # Mock secrets
        mock_get_secret.side_effect = lambda x, y=None: "dummy_value"
        
        # Mock Client instance
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.get_mode.return_value = "emergency_backup" # Already in backup

        # Mock time to 00:05
        tz = pytz.timezone(config.TIMEZONE)
        mock_now = datetime.datetime(2023, 1, 1, 0, 5, 0, tzinfo=tz)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = datetime.datetime

            # Call the function
            request = MagicMock()
            response = main.mode_switcher(request)
            
            # Verify
            self.assertEqual(response, ("Already in emergency_backup", 200))
            mock_client.set_mode.assert_not_called()

    @patch('main.get_secret')
    @patch('main.TokenFetcher')
    @patch('main.Client')
    def test_no_schedule_match(self, mock_client_cls, mock_fetcher_cls, mock_get_secret):
        # Mock secrets
        mock_get_secret.side_effect = lambda x, y=None: "dummy_value"
        
        # Mock Client instance
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Mock time to 12:00 (no schedule)
        tz = pytz.timezone(config.TIMEZONE)
        mock_now = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=tz)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = datetime.datetime

            # Call the function
            request = MagicMock()
            response = main.mode_switcher(request)
            
            # Verify
            self.assertEqual(response, ("No action taken", 200))
            mock_client.set_mode.assert_not_called()

if __name__ == '__main__':
    unittest.main()
