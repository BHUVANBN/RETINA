#!/usr/bin/env python3
"""
Image Classification Script
Classifies images using the Django app's prediction service
and organizes them into classified subfolders
"""

import os
import sys
import shutil
import numpy as np
from pathlib import Path
import logging

# Setup Django environment
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dr_detection.settings')
import django
django.setup()

from prediction.services import dr_service

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
SOURCE_DIR = Path(__file__).parent / 'colored_images'
OUTPUT_DIR = Path(__file__).parent / 'classified_images'

def setup_output_directory():
    """Create output directory structure"""
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    # Get class labels from the Django service
    class_labels = dr_service.class_labels
    for class_name in class_labels:
        (OUTPUT_DIR / class_name).mkdir(exist_ok=True)
    
    logger.info(f"Created output directory: {OUTPUT_DIR}")
    logger.info(f"Class labels: {class_labels}")

def find_image_files(directory):
    """Find all image files in directory and subdirectories"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    image_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                image_files.append(Path(root) / file)
    
    return image_files

def predict_image_using_django_service(img_path):
    """Predict class for a single image using Django service"""
    try:
        # Open image file and pass to Django service
        with open(img_path, 'rb') as img_file:
            result = dr_service.process_image(img_file)
        
        if not result.get('success', False):
            logger.error(f"Prediction failed for {img_path}: {result.get('error', 'Unknown error')}")
            return None, None
        
        prediction = result['prediction']
        confidence = result['confidence'] / 100.0  # Convert back to decimal
        
        return prediction, confidence
    except Exception as e:
        logger.error(f"Error predicting {img_path}: {e}")
        return None, None

def classify_images():
    """Main classification function"""
    logger.info("Starting image classification using Django app service...")
    logger.info("=" * 50)
    
    # Check source directory
    if not SOURCE_DIR.exists():
        logger.error(f"Source directory not found: {SOURCE_DIR}")
        logger.info("Please add some images to the colored_images folder and run again")
        return
    
    # Find image files
    image_files = find_image_files(SOURCE_DIR)
    if not image_files:
        logger.warning(f"No image files found in {SOURCE_DIR}")
        logger.info("Please add some images to the colored_images folder and run again")
        return
    
    logger.info(f"Found {len(image_files)} images to classify")
    
    # Setup output directory
    setup_output_directory()
    
    # Classify each image
    results = {class_name: 0 for class_name in dr_service.class_labels}
    processed = 0
    
    for img_path in image_files:
        logger.info(f"Processing: {img_path.name}")
        
        predicted_class, confidence = predict_image_using_django_service(img_path)
        
        if predicted_class:
            # Copy image to classified folder
            dest_path = OUTPUT_DIR / predicted_class / img_path.name
            shutil.copy2(img_path, dest_path)
            
            results[predicted_class] += 1
            processed += 1
            
            logger.info(f"  Classified as: {predicted_class} (confidence: {confidence:.2%})")
        else:
            logger.warning(f"  Failed to classify {img_path.name}")
    
    # Print summary
    logger.info(f"\nClassification complete!")
    logger.info(f"Total images processed: {processed}")
    logger.info("Results:")
    for class_name, count in results.items():
        logger.info(f"  {class_name}: {count} images")
    
    logger.info(f"Classified images saved to: {OUTPUT_DIR}")
    logger.info("These predictions now match the Django web app exactly!")

if __name__ == "__main__":
    classify_images()
