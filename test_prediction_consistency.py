#!/usr/bin/env python3
"""
Test script to verify prediction consistency between classification script and Django app
"""

import sys
import os
import numpy as np
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dr_detection.settings')
import django
django.setup()

from prediction.services import dr_service

# Configuration
IMG_SIZE = (224, 224)
TEST_IMAGES = [
    'classified_images/Mild/0773a1c326ad.png',
    'classified_images/Moderate/0151781fe50b.png',
    'classified_images/No_DR/0151781fe50b.png',
    'classified_images/Severe/0151781fe50b.png',
    'classified_images/Proliferate_DR/0151781fe50b.png'
]

def preprocess_image(img_path):
    """Preprocess image exactly like the classification script"""
    try:
        img = Image.open(img_path).convert('RGB')
        img = img.resize(IMG_SIZE)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize
        return img_array
    except Exception as e:
        print(f"Error preprocessing {img_path}: {e}")
        return None

def test_prediction_consistency():
    """Test if Django app predictions match folder classifications"""
    print("Testing prediction consistency...")
    print("=" * 50)
    
    # Test a few images from each classified folder
    test_cases = [
        ('classified_images/Mild/0773a1c326ad.png', 'Mild'),
        ('classified_images/No_DR/0151781fe50b.png', 'No_DR'),
        ('classified_images/Moderate/000c1434d8d7.png', 'Moderate'),
    ]
    
    for img_path, expected_folder in test_cases:
        if not Path(img_path).exists():
            print(f"❌ Image not found: {img_path}")
            continue
            
        folder_name = Path(img_path).parent.name
        print(f"\n📁 Testing image from: {folder_name}")
        print(f"📄 Image: {Path(img_path).name}")
        
        # Preprocess image
        img_array = preprocess_image(img_path)
        if img_array is None:
            print("❌ Failed to preprocess image")
            continue
        
        # Get prediction from Django service
        try:
            # Create a file-like object for the Django service
            with open(img_path, 'rb') as img_file:
                result = dr_service.process_image(img_file)
            
            if not result.get('success', False):
                print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
                continue
            
            prediction = result['prediction']
            confidence = result['confidence'] / 100.0  # Convert back to decimal
                
            print(f"🔮 Predicted: {prediction}")
            print(f"📊 Confidence: {confidence:.2%}")
            
            # Check if prediction matches folder
            if prediction == expected_folder:
                print("✅ Prediction matches folder classification")
            else:
                print(f"❌ MISMATCH! Folder: {expected_folder}, Predicted: {prediction}")
                
        except Exception as e:
            print(f"❌ Error getting prediction: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_prediction_consistency()
