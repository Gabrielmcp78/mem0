"""
Unit tests for Apple Intelligence Foundation Models interface
"""

import unittest
from unittest.mock import patch, MagicMock
import platform
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mem0.utils.apple_intelligence import (
    FoundationModelsInterface,
    get_foundation_models_interface,
    check_apple_intelligence_availability,
    get_apple_intelligence_status,
    AppleIntelligenceError,
    AppleIntelligenceUnavailableError
)


class TestFoundationModelsInterface(unittest.TestCase):
    """Test cases for FoundationModelsInterface"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Reset global instance for each test
        import mem0.utils.apple_intelligence
        mem0.utils.apple_intelligence._foundation_models_interface = None
    
    @patch('platform.system')
    def test_non_macos_system(self, mock_system):
        """Test behavior on non-macOS systems"""
        mock_system.return_value = 'Linux'
        
        interface = FoundationModelsInterface()
        self.assertFalse(interface.is_available)
        self.assertIn("only available on macOS", interface.error_message)
    
    @patch('platform.system')
    @patch('platform.mac_ver')
    def test_old_macos_version(self, mock_mac_ver, mock_system):
        """Test behavior on old macOS versions"""
        mock_system.return_value = 'Darwin'
        mock_mac_ver.return_value = ('14.0', '', '')
        
        interface = FoundationModelsInterface()
        self.assertFalse(interface.is_available)
        self.assertIn("requires macOS 15.1+", interface.error_message)
    
    @patch('platform.system')
    @patch('platform.mac_ver')
    @patch('platform.machine')
    @patch('builtins.__import__')
    def test_apple_silicon_availability(self, mock_import, mock_machine, mock_mac_ver, mock_system):
        """Test availability detection on Apple Silicon"""
        mock_system.return_value = 'Darwin'
        mock_mac_ver.return_value = ('15.1', '', '')
        mock_machine.return_value = 'arm64'
        
        # Mock objc import to succeed
        def mock_import_func(name, *args, **kwargs):
            if name == 'objc':
                mock_objc = MagicMock()
                mock_objc.loadBundle = MagicMock(return_value=MagicMock())
                return mock_objc
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = mock_import_func
        
        interface = FoundationModelsInterface()
        # Should be available on Apple Silicon with macOS 15.1+
        self.assertTrue(interface.is_available)
    
    @patch('platform.system')
    @patch('platform.mac_ver')
    def test_missing_pyobjc(self, mock_mac_ver, mock_system):
        """Test behavior when PyObjC is not available"""
        mock_system.return_value = 'Darwin'
        mock_mac_ver.return_value = ('15.1', '', '')
        
        with patch('builtins.__import__', side_effect=ImportError("No module named 'objc'")):
            interface = FoundationModelsInterface()
            self.assertFalse(interface.is_available)
            self.assertIn("PyObjC is required", interface.error_message)
    
    def test_ensure_available_when_unavailable(self):
        """Test ensure_available raises exception when unavailable"""
        with patch('platform.system', return_value='Linux'):
            interface = FoundationModelsInterface()
            
            with self.assertRaises(AppleIntelligenceUnavailableError):
                interface.ensure_available()
    
    @patch('platform.system')
    @patch('platform.mac_ver')
    @patch('platform.machine')
    @patch('builtins.__import__')
    def test_text_generation(self, mock_import, mock_machine, mock_mac_ver, mock_system):
        """Test text generation functionality"""
        mock_system.return_value = 'Darwin'
        mock_mac_ver.return_value = ('15.1', '', '')
        mock_machine.return_value = 'arm64'
        
        # Mock objc import to succeed
        def mock_import_func(name, *args, **kwargs):
            if name == 'objc':
                mock_objc = MagicMock()
                mock_objc.loadBundle = MagicMock(return_value=MagicMock())
                return mock_objc
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = mock_import_func
        
        interface = FoundationModelsInterface()
        
        if interface.is_available:
            response = interface.generate_text("Test prompt")
            self.assertIsInstance(response, str)
            self.assertIn("Apple Intelligence Response", response)
    
    @patch('platform.system')
    @patch('platform.mac_ver')
    @patch('platform.machine')
    @patch('builtins.__import__')
    def test_embedding_generation(self, mock_import, mock_machine, mock_mac_ver, mock_system):
        """Test embedding generation functionality"""
        mock_system.return_value = 'Darwin'
        mock_mac_ver.return_value = ('15.1', '', '')
        mock_machine.return_value = 'arm64'
        
        # Mock objc import to succeed
        def mock_import_func(name, *args, **kwargs):
            if name == 'objc':
                mock_objc = MagicMock()
                mock_objc.loadBundle = MagicMock(return_value=MagicMock())
                return mock_objc
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = mock_import_func
        
        interface = FoundationModelsInterface()
        
        if interface.is_available:
            embeddings = interface.generate_embeddings("Test text")
            self.assertIsInstance(embeddings, list)
            self.assertEqual(len(embeddings), 1536)  # Default dimensions
            
            # Test custom dimensions
            custom_embeddings = interface.generate_embeddings("Test text", dimensions=512)
            self.assertEqual(len(custom_embeddings), 512)
    
    def test_system_info(self):
        """Test system information retrieval"""
        interface = FoundationModelsInterface()
        sys_info = interface.get_system_info()
        
        self.assertIsInstance(sys_info, dict)
        self.assertIn('available', sys_info)
        self.assertIn('platform', sys_info)
        self.assertIn('machine', sys_info)
        self.assertIn('python_version', sys_info)
    
    def test_global_interface_singleton(self):
        """Test that global interface returns the same instance"""
        interface1 = get_foundation_models_interface()
        interface2 = get_foundation_models_interface()
        
        self.assertIs(interface1, interface2)
    
    def test_availability_check_function(self):
        """Test the standalone availability check function"""
        result = check_apple_intelligence_availability()
        self.assertIsInstance(result, bool)
    
    def test_status_function(self):
        """Test the standalone status function"""
        status = get_apple_intelligence_status()
        self.assertIsInstance(status, dict)
        self.assertIn('available', status)
        self.assertIn('platform', status)


class TestAppleIntelligenceErrors(unittest.TestCase):
    """Test cases for Apple Intelligence error handling"""
    
    def test_apple_intelligence_error(self):
        """Test base Apple Intelligence error"""
        error = AppleIntelligenceError("Test error")
        self.assertEqual(str(error), "Test error")
    
    def test_apple_intelligence_unavailable_error(self):
        """Test Apple Intelligence unavailable error"""
        error = AppleIntelligenceUnavailableError("Not available")
        self.assertEqual(str(error), "Not available")
        self.assertIsInstance(error, AppleIntelligenceError)


if __name__ == '__main__':
    unittest.main()