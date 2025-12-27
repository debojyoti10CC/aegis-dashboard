#!/usr/bin/env python3
"""
Create extreme disaster image that should pass verification
"""

import numpy as np
from PIL import Image, ImageDraw
import os

def create_extreme_fire():
    """Create extreme fire disaster"""
    width, height = 640, 480
    
    # Create base image (dark smoky sky)
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Fill most of image with fire colors
    # Create massive fire covering 70% of image
    fire_area = [0, height//3, width, height]
    draw.rectangle(fire_area, fill='red')
    
    # Add orange layer
    orange_area = [20, height//3 + 20, width-20, height-20]
    draw.rectangle(orange_area, fill='orange')
    
    # Add yellow core
    yellow_area = [40, height//3 + 40, width-40, height-40]
    draw.rectangle(yellow_area, fill='yellow')
    
    # Add massive flames reaching to top
    for x in range(0, width, 30):
        flame_height = np.random.randint(100, 200)
        flame_points = [
            (x, height//3),
            (x + 10, height//3 - flame_height),
            (x + 20, height//3 - flame_height - 20),
            (x + 30, height//3 - flame_height),
            (x + 40, height//3)
        ]
        colors = ['red', 'orange', 'yellow']
        color = colors[np.random.randint(0, 3)]
        draw.polygon(flame_points, fill=color)
    
    # Add thick smoke covering upper portion
    smoke_area = [0, 0, width, height//2]
    draw.rectangle(smoke_area, fill='gray')
    
    # Add darker smoke patches
    for _ in range(10):
        x = np.random.randint(0, width-100)
        y = np.random.randint(0, height//2)
        w = np.random.randint(50, 150)
        h = np.random.randint(30, 80)
        draw.ellipse([x, y, x+w, y+h], fill='darkgray')
    
    return img

def main():
    """Create extreme disaster image"""
    os.makedirs('test_images', exist_ok=True)
    
    # Create extreme fire
    extreme_fire = create_extreme_fire()
    extreme_fire.save('test_images/extreme_fire.jpg', 'JPEG')
    print("✅ Created test_images/extreme_fire.jpg")
    
    print("\n🔥 Extreme disaster image created!")

if __name__ == '__main__':
    main()