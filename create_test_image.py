#!/usr/bin/env python3
"""
Create a simple test image for disaster detection
"""

import numpy as np
from PIL import Image, ImageDraw
import os

def create_fire_test_image():
    """Create a simple fire-like test image"""
    # Create a 640x480 image
    width, height = 640, 480
    
    # Create base image (landscape)
    img = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw ground
    draw.rectangle([0, height//2, width, height], fill='green')
    
    # Draw fire-like areas (red/orange)
    fire_areas = [
        [100, 200, 200, 300],  # Fire area 1
        [300, 150, 450, 280],  # Fire area 2
        [500, 180, 600, 320],  # Fire area 3
    ]
    
    for area in fire_areas:
        # Draw fire base (red)
        draw.ellipse(area, fill='red')
        
        # Draw flames (orange/yellow)
        flame_x = area[0] + (area[2] - area[0]) // 2
        flame_y = area[1]
        flame_width = (area[2] - area[0]) // 3
        
        # Multiple flame shapes
        for i in range(3):
            flame_points = [
                (flame_x - flame_width//2 + i*10, area[1]),
                (flame_x - flame_width//4 + i*10, area[1] - 30),
                (flame_x + i*10, area[1] - 50),
                (flame_x + flame_width//4 + i*10, area[1] - 30),
                (flame_x + flame_width//2 + i*10, area[1])
            ]
            draw.polygon(flame_points, fill='orange')
    
    # Add some smoke (gray areas)
    smoke_areas = [
        [150, 100, 250, 200],
        [350, 80, 480, 180],
    ]
    
    for area in smoke_areas:
        draw.ellipse(area, fill='gray')
    
    return img

def create_flood_test_image():
    """Create a simple flood-like test image"""
    width, height = 640, 480
    
    # Create base image
    img = Image.new('RGB', (width, height), color='lightgray')
    draw = ImageDraw.Draw(img)
    
    # Draw sky
    draw.rectangle([0, 0, width, height//3], fill='lightblue')
    
    # Draw flood water (blue covering most of the image)
    draw.rectangle([0, height//3, width, height], fill='blue')
    
    # Draw some buildings partially submerged
    buildings = [
        [50, 100, 120, 400],   # Building 1
        [200, 80, 280, 420],   # Building 2
        [400, 120, 480, 450],  # Building 3
    ]
    
    for building in buildings:
        draw.rectangle(building, fill='brown')
        # Windows
        for i in range(2, 8):
            for j in range(1, 4):
                window_x = building[0] + j * 20
                window_y = building[1] + i * 30
                if window_y < height//3 + 50:  # Above water line
                    draw.rectangle([window_x, window_y, window_x+15, window_y+20], fill='yellow')
    
    return img

def main():
    """Create test images"""
    # Create test_images directory
    os.makedirs('test_images', exist_ok=True)
    
    # Create fire test image
    fire_img = create_fire_test_image()
    fire_img.save('test_images/fire_disaster.jpg', 'JPEG')
    print("✅ Created test_images/fire_disaster.jpg")
    
    # Create flood test image
    flood_img = create_flood_test_image()
    flood_img.save('test_images/flood_disaster.jpg', 'JPEG')
    print("✅ Created test_images/flood_disaster.jpg")
    
    print("\n🧪 Test images created successfully!")
    print("You can now test the system with:")
    print("python run.py test test_images/fire_disaster.jpg --coordinates '34.0522,-118.2437'")
    print("python run.py test test_images/flood_disaster.jpg --coordinates '29.7604,-95.3698'")

if __name__ == '__main__':
    main()