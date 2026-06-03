
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import asyncio

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing app modules
sys.modules['app.core.database'] = MagicMock()
sys.modules['app.models.models'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['fastapi'] = MagicMock()
sys.modules['app.services.fingerprint'] = MagicMock()
sys.modules['app.services.file_handler'] = MagicMock()
sys.modules['app.services.visualize'] = MagicMock()

# Now import the module to test
# We need to use importlib to reload if it was already partially imported
import importlib
if 'app.api.recognize' in sys.modules:
    importlib.reload(sys.modules['app.api.recognize'])
else:
    from app.api.recognize import recognize_song

class TestConfidenceNormalization(unittest.IsolatedAsyncioTestCase):
    async def test_confidence_normalization(self):
        # Mock dependencies
        mock_file = MagicMock()
        mock_file.filename = "test.mp3"
        # Make read awaitable
        mock_file.read = AsyncMock(return_value=b"fake audio content")
        
        mock_db = MagicMock()
        
        # Mock fingerprint_audio to return a known number of fingerprints
        with patch('app.api.recognize.fingerprint_audio') as mock_fingerprint, \
             patch('app.api.recognize.match_fingerprints') as mock_match, \
             patch('app.api.recognize.validate_audio_file', new_callable=AsyncMock) as mock_validate, \
             patch('app.api.recognize.save_audio_file') as mock_save, \
             patch('builtins.open', new_callable=MagicMock), \
             patch('os.remove'), \
             patch('os.path.exists', return_value=True):
            
            # 100 query fingerprints
            mock_fingerprint.return_value = [('hash', i) for i in range(100)]
            
            # Match returns a raw confidence score of 50
            # If logic is correct, normalized confidence should be 50 / 100 = 0.5
            mock_match.return_value = {
                1: {
                    'matches': 10,
                    'confidence': 50.0,
                    'avg_time_offset': 10.0
                }
            }
            
            # Mock DB query for song details
            mock_song = MagicMock()
            mock_song.id = 1
            mock_song.title = "Test Song"
            mock_song.artist.name = "Test Artist"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_song
            
            # Run the function
            result = await recognize_song(mock_file, mock_db)
            
            # Verify results
            self.assertTrue(result['success'])
            self.assertEqual(len(result['matches']), 1)
            match = result['matches'][0]
            
            print(f"Raw confidence: 50.0")
            print(f"Query fingerprints: 100")
            print(f"Result confidence: {match['confidence']}")
            
            # Check if confidence is normalized
            self.assertEqual(match['confidence'], 0.5)
            self.assertLessEqual(match['confidence'], 1.0)

    async def test_confidence_clamping(self):
        # Test that confidence doesn't exceed 1.0
        mock_file = MagicMock()
        mock_file.filename = "test.mp3"
        # Make read awaitable
        mock_file.read = AsyncMock(return_value=b"fake audio content")

        mock_db = MagicMock()
        
        with patch('app.api.recognize.fingerprint_audio') as mock_fingerprint, \
             patch('app.api.recognize.match_fingerprints') as mock_match, \
             patch('app.api.recognize.validate_audio_file', new_callable=AsyncMock) as mock_validate, \
             patch('builtins.open', new_callable=MagicMock), \
             patch('os.remove'), \
             patch('os.path.exists', return_value=True):
            
            # 50 query fingerprints
            mock_fingerprint.return_value = [('hash', i) for i in range(50)]
            
            # Match returns a raw confidence score of 100 (impossible in reality but good for testing clamping)
            # 100 / 50 = 2.0, should be clamped to 1.0
            mock_match.return_value = {
                1: {
                    'matches': 50,
                    'confidence': 100.0,
                    'avg_time_offset': 10.0
                }
            }
            
            mock_song = MagicMock()
            mock_song.id = 1
            mock_song.title = "Test Song"
            mock_song.artist.name = "Test Artist"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_song
            
            result = await recognize_song(mock_file, mock_db)
            
            match = result['matches'][0]
            print(f"Raw confidence: 100.0")
            print(f"Query fingerprints: 50")
            print(f"Result confidence: {match['confidence']}")
            
            self.assertEqual(match['confidence'], 1.0)

if __name__ == '__main__':
    unittest.main()
