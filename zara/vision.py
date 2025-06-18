"""
Vision system for Zara Assistant.
Handles image processing and computer vision tasks.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
import time
import json

from .logger import get_logger

logger = get_logger()

class VisionSystem:
    """Handles computer vision tasks using OpenCV and deep learning models."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize vision system and load models."""
        try:
            self.models_dir = Path("models")
            self.models_dir.mkdir(exist_ok=True)
            
            # Load class labels
            self.labels_path = self.models_dir / "coco.names"
            self.labels = self._load_labels()
            
            # Load neural network
            self.net = self._load_neural_network()
            
            logger.info("Vision system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vision system: {str(e)}")
            raise
    
    def _load_labels(self) -> List[str]:
        """Load COCO class labels."""
        try:
            if not self.labels_path.exists():
                raise FileNotFoundError(f"Labels file not found: {self.labels_path}")
            
            with open(self.labels_path) as f:
                labels = [line.strip() for line in f.readlines()]
            logger.info(f"Loaded {len(labels)} class labels")
            return labels
        
        except Exception as e:
            logger.error(f"Failed to load labels: {str(e)}")
            raise
    
    def _load_neural_network(self) -> cv2.dnn.Net:
        """Load and configure MobileNetSSD neural network."""
        try:
            prototxt_path = Path("MobileNetSSD_deploy.prototxt")
            model_path = self.models_dir / "MobileNetSSD_deploy.caffemodel"
            
            if not prototxt_path.exists():
                raise FileNotFoundError(f"Prototxt file not found: {prototxt_path}")
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            net = cv2.dnn.readNetFromCaffe(
                str(prototxt_path),
                str(model_path)
            )
            logger.info("Neural network loaded successfully")
            return net
        
        except Exception as e:
            logger.error(f"Failed to load neural network: {str(e)}")
            raise
    
    def process_image(self, image_path: Union[str, Path], 
                     tasks: List[str] = None) -> Dict[str, Any]:
        """Process image with specified tasks."""
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Failed to read image: {image_path}")
            
            results = {}
            tasks = tasks or ["object_detection"]  # Default to object detection
            
            # Process each requested task
            for task in tasks:
                task_fn = getattr(self, f"_task_{task}", None)
                if task_fn:
                    results[task] = task_fn(image)
                else:
                    logger.warning(f"Unsupported vision task: {task}")
            
            return results
        
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return {"error": str(e)}
    
    def _task_object_detection(self, image: np.ndarray) -> Dict[str, List[Dict]]:
        """Detect objects in image using MobileNetSSD."""
        try:
            height, width = image.shape[:2]
            
            # Prepare image for neural network
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)),
                0.007843,
                (300, 300),
                127.5
            )
            
            # Detect objects
            self.net.setInput(blob)
            detections = self.net.forward()
            
            results = []
            confidence_threshold = 0.2
            
            # Process detections
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > confidence_threshold:
                    class_id = int(detections[0, 0, i, 1])
                    
                    if class_id < len(self.labels):
                        box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                        (startX, startY, endX, endY) = box.astype("int")
                        
                        results.append({
                            "label": self.labels[class_id],
                            "confidence": float(confidence),
                            "box": {
                                "x1": int(startX),
                                "y1": int(startY),
                                "x2": int(endX),
                                "y2": int(endY)
                            }
                        })
            
            logger.info(f"Detected {len(results)} objects")
            return {"detections": results}
        
        except Exception as e:
            logger.error(f"Object detection failed: {str(e)}")
            return {"error": str(e)}
    
    def _task_text_detection(self, image: np.ndarray) -> Dict[str, List[str]]:
        """Detect and recognize text in image."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Simple thresholding for text detection
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(
                binary,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Extract potential text regions
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 20:  # Filter small regions
                    text_regions.append({
                        "box": {
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h)
                        }
                    })
            
            logger.info(f"Found {len(text_regions)} potential text regions")
            return {"text_regions": text_regions}
        
        except Exception as e:
            logger.error(f"Text detection failed: {str(e)}")
            return {"error": str(e)}
    
    def _task_face_detection(self, image: np.ndarray) -> Dict[str, List[Dict]]:
        """Detect faces in image using Haar Cascade."""
        try:
            # Load face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Process results
            results = []
            for (x, y, w, h) in faces:
                results.append({
                    "box": {
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h)
                    }
                })
            
            logger.info(f"Detected {len(results)} faces")
            return {"faces": results}
        
        except Exception as e:
            logger.error(f"Face detection failed: {str(e)}")
            return {"error": str(e)}
    
    def capture_screenshot(self, save_path: Optional[Path] = None) -> Optional[str]:
        """Capture screenshot using OpenCV."""
        try:
            import pyautogui
            
            # Capture screen
            screenshot = pyautogui.screenshot()
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            if save_path:
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(save_path), image)
                logger.info(f"Screenshot saved to {save_path}")
                return str(save_path)
            
            return None
        
        except Exception as e:
            logger.error(f"Screenshot capture failed: {str(e)}")
            return None

# Convenience function to get the vision system instance
def get_vision_system() -> VisionSystem:
    """Get the singleton vision system instance."""
    return VisionSystem()