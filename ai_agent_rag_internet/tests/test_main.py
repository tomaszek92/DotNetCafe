import unittest
from unittest.mock import patch, MagicMock
from src.main import parse_recommendation, get_recommendations, get_cultural_events

class TestMain(unittest.TestCase):

    def test_parse_recommendation(self):
        # Test with a valid input
        recommendation = "Paris, France"
        city, country = parse_recommendation(recommendation)
        self.assertEqual(city, "Paris")
        self.assertEqual(country, "France")

        # Test with an invalid input
        recommendation = "InvalidFormat"
        city, country = parse_recommendation(recommendation)
        self.assertIsNone(city)
        self.assertIsNone(country)

    @patch('src.main.requests.post')
    @patch('src.main.get_cultural_events')  # Mock get_cultural_events to avoid calling it
    def test_get_recommendations(self, mock_get_cultural_events, mock_post):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Paris, France'}}]
        }
        mock_post.return_value = mock_response

        # Test the function
        config = {'API_KEYS': {'openai_api_key': 'fake_key', 'brave_api_key': 'fake_key'}}
        user_data = [{'location': {'city': 'Barcelona', 'country': 'Spain'}}]
        get_recommendations(user_data, config)

        # Check if the API was called
        mock_post.assert_called_once()
        mock_get_cultural_events.assert_called_once_with('Paris', 'France', config)

    @patch('src.main.requests.get')
    def test_get_cultural_events(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'web': {'results': [{'title': 'Event 1', 'url': 'http://example.com', 'description': 'Description 1'}]}
        }
        mock_get.return_value = mock_response

        # Test the function
        config = {'API_KEYS': {'brave_api_key': 'fake_key'}}
        get_cultural_events('Paris', 'France', config)

        # Check if the API was called
        mock_get.assert_called_once()

if __name__ == '__main__':
    unittest.main() 