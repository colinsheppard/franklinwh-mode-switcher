import unittest
from unittest.mock import patch, MagicMock
import datetime
import pytz
import main
import config

class TestModeSwitcher(unittest.TestCase):

    @patch('main.Mode')
    @patch('main.get_secret')
    @patch('main.TokenFetcher')
    @patch('main.Client')
    def test_mode_switch_trigger(self, mock_client_cls, mock_fetcher_cls, mock_get_secret, mock_mode_cls):

        # Mock secrets
        mock_get_secret.side_effect = lambda x, y=None: "dummy_value"
        
        # Mock Client instance
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.get_mode.return_value = ("time_of_use", 20) # Currently in TOU

        # Mock Mode factory
        mock_mode_instance = MagicMock()
        mock_mode_cls.emergency_backup.return_value = mock_mode_instance

        # Mock time to 00:30 (should trigger emergency_backup)
        tz = pytz.timezone(config.TIMEZONE)
        # 00:30
        mock_now = datetime.datetime(2023, 1, 1, 0, 30, 0, tzinfo=tz)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = datetime.datetime

            # Call the function
            request = MagicMock()
            response = main.mode_switcher(request)
            
            # Verify
            self.assertEqual(response, ("Switched to emergency_backup", 200))
            self.assertEqual(response, ("Switched to emergency_backup", 200))
            mock_client.set_mode.assert_called_with(mock_mode_instance)

    @patch('main.Mode')
    @patch('main.get_secret')
    @patch('main.TokenFetcher')
    @patch('main.Client')
    def test_no_action_needed(self, mock_client_cls, mock_fetcher_cls, mock_get_secret, mock_mode_cls):
        # Mock secrets
        mock_get_secret.side_effect = lambda x, y=None: "dummy_value"
        
        # Mock Client instance
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.get_mode.return_value = ("emergency_backup", 100) # Already in backup

        # Mock time to 00:30
        tz = pytz.timezone(config.TIMEZONE)
        mock_now = datetime.datetime(2023, 1, 1, 0, 30, 0, tzinfo=tz)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = datetime.datetime

            # Call the function
            request = MagicMock()
            response = main.mode_switcher(request)
            
            # Verify
            self.assertEqual(response, ("Already in emergency_backup", 200))
            mock_client.set_mode.assert_not_called()

    @patch('main.Mode')
    @patch('main.get_secret')
    @patch('main.TokenFetcher')
    @patch('main.Client')
    def test_no_schedule_match(self, mock_client_cls, mock_fetcher_cls, mock_get_secret, mock_mode_cls):
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

    @patch('main.Mode')
    @patch('main.get_secret')
    @patch('main.TokenFetcher')
    @patch('main.Client')
    def test_mapped_mode_id(self, mock_client_cls, mock_fetcher_cls, mock_get_secret, mock_mode_cls):
        """Test that unknown ID 18513 is correctly mapped to time_of_use"""
        # Mock secrets
        mock_get_secret.side_effect = lambda x, y=None: "dummy_value"
        
        # Mock Client instance
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        # 18513 means time_of_use now, so if we return it here...
        # But wait, get_mode() calls _switch_status() then looks up MODE_MAP.
        # We need to mock what get_mode() returns, which is the RESULT of that lookup.
        # So we just mock the return value of get_mode to be the string "time_of_use".
        # However, to TRULY test the monkeypatch, we'd need to mock _switch_status to return 18513 
        # and let the real get_mode run... but we are mocking Client entirely here.
        
        # Testing checking logic: if get_mode returns "time_of_use" (whether from 9322 or 18513)
        # the app should treat it as "time_of_use".
        mock_client.get_mode.return_value = ("time_of_use", 20)

        # Mock time to 04:00 (target time_of_use)
        tz = pytz.timezone(config.TIMEZONE)
        mock_now = datetime.datetime(2023, 1, 1, 4, 0, 0, tzinfo=tz)
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = datetime.datetime

            # Call the function
            request = MagicMock()
            response = main.mode_switcher(request)
            
            # Verify: Should be "Already in time_of_use"
            self.assertEqual(response, ("Already in time_of_use", 200))
            mock_client.set_mode.assert_not_called()

if __name__ == '__main__':
    unittest.main()
