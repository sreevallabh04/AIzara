"""
Test suite for Zara's vision system.
Tests image processing, object detection, and computer vision tasks.
"""

import pytest
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from zara.vision import get_vision_system, VisionSystem

# Mock image data
MOCK_IMAGE = np.zeros((300, 300, 3), dtype=np.uint8)
MOCK_DETECTIONS = np.array([
    [0, 1, 0.95, 0.1, 0.2, 0.3, 0.4]  # [img_id, class_id, confidence, x1, y1, x2, y2]
])

@pytest.fixture
def mock_cv2():
    """Mock OpenCV functionality."""
    with patch('cv2.dnn.readNetFromCaffe') as mock_read_net, \
         patch('cv2.imread', return_value=MOCK_IMAGE), \
         patch('cv2.resize', return_value=MOCK_IMAGE), \
         patch('cv2.dnn.blobFromImage', return_value=np.zeros((1, 3, 300, 300))), \
         patch('cv2.cvtColor', return_value=MOCK_IMAGE):
        
        # Configure mock neural network
        mock_net = MagicMock()
        mock_net.forward.return_value = MOCK_DETECTIONS
        mock_read_net.return_value = mock_net
        
        yield {
            'read_net': mock_read_net,
            'net': mock_net
        }

@pytest.fixture
def mock_labels(tmp_path):
    """Create mock COCO labels file."""
    labels = ['background', 'person', 'car', 'dog']
    labels_file = tmp_path / "coco.names"
    labels_file.write_text('\n'.join(labels))
    return labels_file

@pytest.fixture
def mock_models(tmp_path):
    """Create mock model files."""
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    
    # Create dummy model files
    (models_dir / "MobileNetSSD_deploy.caffemodel").touch()
    prototxt = Path("MobileNetSSD_deploy.prototxt")
    prototxt.touch()
    
    return models_dir

@pytest.fixture
def test_vision(mock_cv2, mock_labels, mock_models, tmp_path):
    """Create test vision system instance."""
    # Reset singleton
    VisionSystem._instance = None
    
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.mkdir'):
        return get_vision_system()

def test_vision_singleton():
    """Test that vision system is a singleton."""
    vision1 = get_vision_system()
    vision2 = get_vision_system()
    assert vision1 is vision2

def test_model_initialization(test_vision, mock_cv2):
    """Test neural network initialization."""
    assert test_vision.net is not None
    mock_cv2['read_net'].assert_called_once()

def test_labels_loading(test_vision, mock_labels):
    """Test COCO labels loading."""
    assert len(test_vision.labels) == 4
    assert 'person' in test_vision.labels
    assert 'car' in test_vision.labels

def test_object_detection(test_vision):
    """Test object detection functionality."""
    test_image = np.zeros((500, 500, 3), dtype=np.uint8)
    results = test_vision._task_object_detection(test_image)
    
    assert 'detections' in results
    assert len(results['detections']) == 1
    
    detection = results['detections'][0]
    assert detection['label'] == 'person'  # Class ID 1
    assert detection['confidence'] > 0.9
    assert all(k in detection['box'] for k in ['x1', 'y1', 'x2', 'y2'])

def test_text_detection(test_vision):
    """Test text detection functionality."""
    test_image = np.zeros((500, 500, 3), dtype=np.uint8)
    results = test_vision._task_text_detection(test_image)
    
    assert 'text_regions' in results
    for region in results['text_regions']:
        assert all(k in region['box'] for k in ['x', 'y', 'width', 'height'])

def test_face_detection(test_vision):
    """Test face detection functionality."""
    with patch('cv2.CascadeClassifier') as mock_cascade:
        mock_cascade.return_value.detectMultiScale.return_value = np.array([[10, 20, 100, 100]])
        
        test_image = np.zeros((500, 500, 3), dtype=np.uint8)
        results = test_vision._task_face_detection(test_image)
        
        assert 'faces' in results
        assert len(results['faces']) == 1
        face = results['faces'][0]
        assert all(k in face['box'] for k in ['x', 'y', 'width', 'height'])

def test_screenshot_capture(test_vision):
    """Test screenshot functionality."""
    with patch('pyautogui.screenshot') as mock_screenshot:
        mock_screenshot.return_value = MagicMock(
            size=(1920, 1080),
            tobytes=lambda: np.zeros((1080, 1920, 3), dtype=np.uint8).tobytes()
        )
        
        save_path = Path("test_screenshot.png")
        result = test_vision.capture_screenshot(save_path)
        assert result == str(save_path)

def test_process_image_missing_file(test_vision):
    """Test handling of missing image file."""
    results = test_vision.process_image("nonexistent.jpg")
    assert 'error' in results
    assert 'not found' in results['error']

def test_process_image_invalid_task(test_vision):
    """Test handling of invalid task type."""
    test_image = np.zeros((500, 500, 3), dtype=np.uint8)
    with patch('pathlib.Path.exists', return_value=True), \
         patch('cv2.imread', return_value=test_image):
        results = test_vision.process_image("test.jpg", tasks=["invalid_task"])
        assert not results.get("invalid_task")

def test_process_image_multiple_tasks(test_vision):
    """Test processing multiple tasks for one image."""
    test_image = np.zeros((500, 500, 3), dtype=np.uint8)
    with patch('pathlib.Path.exists', return_value=True), \
         patch('cv2.imread', return_value=test_image):
        results = test_vision.process_image(
            "test.jpg",
            tasks=["object_detection", "face_detection"]
        )
        assert "object_detection" in results
        assert "face_detection" in results

def test_error_handling(test_vision):
    """Test error handling in vision tasks."""
    # Test neural network error
    test_vision.net.forward.side_effect = Exception("Network error")
    results = test_vision._task_object_detection(MOCK_IMAGE)
    assert 'error' in results
    assert 'Network error' in results['error']

def test_confidence_threshold(test_vision):
    """Test confidence threshold in object detection."""
    # Create detections with varying confidences
    low_conf_detection = np.array([[0, 1, 0.1, 0.1, 0.2, 0.3, 0.4]])
    test_vision.net.forward.return_value = low_conf_detection
    
    results = test_vision._task_object_detection(MOCK_IMAGE)
    assert len(results['detections']) == 0  # Should filter out low confidence

def test_image_preprocessing(test_vision):
    """Test image preprocessing for neural network."""
    test_image = np.zeros((500, 500, 3), dtype=np.uint8)
    with patch('cv2.dnn.blobFromImage') as mock_blob:
        test_vision._task_object_detection(test_image)
        mock_blob.assert_called_once()
        # Verify preprocessing parameters
        args = mock_blob.call_args[0]
        assert args[1] == 0.007843  # Scale factor
        assert args[2] == (300, 300)  # Size
        assert args[3] == 127.5  # Mean subtraction

def test_concurrent_processing(test_vision):
    """Test handling multiple concurrent image processing requests."""
    import threading
    
    def process_image():
        results = test_vision.process_image("test.jpg", tasks=["object_detection"])
        assert 'object_detection' in results
    
    threads = [
        threading.Thread(target=process_image)
        for _ in range(3)
    ]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()