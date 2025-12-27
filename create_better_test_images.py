#!/usr/bin/env python3
"""
Create better test images for disaster detection
"""

import numpy as np
from PIL import Image, ImageDraw
import os

def create_intense_fire_image():
    """Create a more intense fire image"""
    width, height = 640, 480
    
    # Create base image (dark sky)
    img = Image.new('RGB', (width, height), color='darkgray')
    draw = ImageDraw.Draw(img)
    
    # Draw ground
    draw.rectangle([0, height//2, width, height], fill='brown')
    
    # Create large fire areas with more red/orange
    fire_areas = [
        [50, 150, 250, 400],   # Large fire 1
        [200, 100, 450, 350],  # Large fire 2
        [350, 120, 580, 380],  # Large fire 3
    ]
    
    for area in fire_areas:
        # Draw fire base (bright red)
        draw.ellipse(area, fill='red')
        
        # Add orange layer
        inner_area = [area[0]+20, area[1]+20, area[2]-20, area[3]-20]
        draw.ellipse(inner_area, fill='orange')
        
        # Add yellow core
        core_area = [area[0]+40, area[1]+40, area[2]-40, area[3]-40]
        draw.ellipse(core_area, fill='yellow')
        
        # Draw tall flames
        flame_x = area[0] + (area[2] - area[0]) // 2
        flame_y = area[1]
        
        for i in range(5):
            flame_points = [
                (flame_x - 30 + i*15, area[1]),
                (flame_x - 15 + i*15, area[1] - 80),
                (flame_x + i*15, area[1] - 120),
                (flame_x + 15 + i*15, area[1] - 80),
                (flame_x + 30 + i*15, area[1])
            ]
            colors = ['red', 'orange', 'yellow', 'orange', 'red']
            draw.polygon(flame_points, fill=colors[i])
    
    # Add lots of smoke (gray areas)
    smoke_areas = [
        [100, 50, 300, 180],
        [250, 30, 500, 160],
        [400, 40, 600, 170],
    ]
    
    for area in smoke_areas:
        draw.ellipse(area, fill='gray')
        # Add darker smoke
        inner_smoke = [area[0]+10, area[1]+10, area[2]-10, area[3]-10]
        draw.ellipse(inner_smoke, fill='darkgray')
    
    return img

def create_structural_damage_image():
    """Create structural damage image"""
    width, height = 640, 480
    
    # Create base image
    img = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw ground with debris
    draw.rectangle([0, height//2, width, height], fill='gray')
    
    # Draw damaged buildings
    buildings = [
        [50, 200, 150, 450],   # Collapsed building
        [200, 150, 300, 400],  # Tilted building
        [350, 180, 450, 420],  # Partially collapsed
    ]
    
    for i, building in enumerate(buildings):
        # Draw building with damage
        if i == 0:  # Collapsed
            # Draw rubble pile
            draw.polygon([
                (building[0], building[3]),
                (building[0]+30, building[1]+100),
                (building[2]-20, building[1]+80),
                (building[2], building[3])
            ], fill='brown')
        elif i == 1:  # Tilted
            # Draw tilted rectangle
            draw.polygon([
                (building[0], building[3]),
                (building[0]+20, building[1]),
                (building[2]+30, building[1]+20),
                (building[2], building[3])
            ], fill='brown')
        else:  # Partially collapsed
            # Draw normal building with hole
            draw.rectangle(building, fill='brown')
            # Add hole/damage
            hole = [building[0]+20, building[1]+50, building[2]-20, building[3]-100]
            draw.ellipse(hole, fill='black')
    
    # Add debris scattered around
    for _ in range(20):
        x = np.random.randint(0, width-20)
        y = np.random.randint(height//2, height-20)
        size = np.random.randint(5, 15)
        draw.rectangle([x, y, x+size, y+size], fill='darkgray')
    
    return img

def main():
    """Create better test images"""
    os.makedirs('test_images', exist_ok=True)
    
    # Create intense fire image
    fire_img = create_intense_fire_image()
    fire_img.save('test_images/intense_fire.jpg', 'JPEG')
    print("✅ Created test_images/intense_fire.jpg")
    
    # Create structural damage image
    damage_img = create_structural_damage_image()
    damage_img.save('test_images/structural_damage.jpg', 'JPEG')
    print("✅ Created test_images/structural_damage.jpg")
    
    print("\n🧪 Better test images created!")
    print("Test with:")
    print("python test_disaster_detection.py")

if __name__ == '__main__':
    main()