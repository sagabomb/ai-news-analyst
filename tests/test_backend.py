import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent folder to path so we can import backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend

class TestFoodieBrain(unittest.TestCase):

    # TEST 1: The "Happy Path" (Everything works)
    @patch('backend.genai.Client') 
    @patch('backend.TavilyClient')
    def test_search_and_analyze_success(self, mock_tavily, mock_genai_client):
        """
        Test updated for Google GenAI SDK v1.0+
        """
        # 1. MOCK TAVILY (Search results)
        mock_t_instance = mock_tavily.return_value
        mock_t_instance.search.return_value = {
            'results': [{'title': 'Pizza Guide', 'content': 'Pizza Nova is the best.'}]
        }

        # 2. MOCK GEMINI (The Brain)
        mock_client_instance = mock_genai_client.return_value
        mock_models = mock_client_instance.models
        
        # Prepare the fake JSON response
        mock_response = MagicMock()
        mock_response.text = """
        [
          {
            "name": "Pizza Nova",
            "neighborhood": "Markham",
            "taste_rating": 8,
            "notes": "Classic slice",
            "confidence_score": 9
          }
        ]
        """
        mock_models.generate_content.return_value = mock_response

        # 3. RUN (With "Open" verification mocked to True)
        with patch('backend.verify_is_open', return_value=True):
            results = backend.search_and_analyze("Pizza", "Markham")

        # 4. VERIFY
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Pizza Nova")

    # TEST 2: The "Safety Check" (Missing API Keys)
    def test_missing_api_keys(self):
        """
        Test that we return empty list gracefully if keys are missing
        """
        # We temporarily set the keys to None inside the backend module
        with patch('backend.TAVILY_API_KEY', None):
            results = backend.search_and_analyze("Pizza", "Markham")
            
            # Should return empty list, not crash
            self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()