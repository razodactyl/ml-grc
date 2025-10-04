#!/usr/bin/env python3
"""
Generate sample images for GRC examples.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random


def create_sample_images():
    """Create sample images with various objects for annotation examples."""
    
    # Create examples directory if it doesn't exist
    os.makedirs("examples/sample_images", exist_ok=True)
    
    # Sample 1: Street scene with cars and people
    create_street_scene()
    
    # Sample 2: Indoor scene with furniture
    create_indoor_scene()
    
    # Sample 3: Nature scene with animals
    create_nature_scene()
    
    # Sample 4: Abstract shapes for testing
    create_abstract_shapes()
    
    print("Sample images created in examples/sample_images/")


def create_street_scene():
    """Create a street scene with cars, people, and traffic signs."""
    img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw road
    draw.rectangle([0, 400, 800, 600], fill='gray')
    
    # Draw cars
    draw.rectangle([100, 450, 200, 500], fill='red')  # Car 1
    draw.rectangle([300, 450, 400, 500], fill='blue')  # Car 2
    draw.rectangle([500, 450, 600, 500], fill='green')  # Car 3
    
    # Draw people
    draw.ellipse([150, 350, 170, 370], fill='pink')  # Person 1 head
    draw.rectangle([160, 370, 170, 420], fill='black')  # Person 1 body
    
    draw.ellipse([350, 350, 370, 370], fill='pink')  # Person 2 head
    draw.rectangle([360, 370, 370, 420], fill='blue')  # Person 2 body
    
    # Draw traffic light
    draw.rectangle([700, 200, 720, 300], fill='black')
    draw.ellipse([705, 210, 715, 220], fill='red')  # Red light
    draw.ellipse([705, 230, 715, 240], fill='yellow')  # Yellow light
    draw.ellipse([705, 250, 715, 260], fill='green')  # Green light
    
    # Draw buildings
    draw.rectangle([0, 100, 200, 400], fill='brown')
    draw.rectangle([200, 150, 400, 400], fill='gray')
    draw.rectangle([400, 120, 600, 400], fill='tan')
    
    img.save('examples/sample_images/street_scene.jpg')


def create_indoor_scene():
    """Create an indoor scene with furniture."""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw room outline
    draw.rectangle([50, 50, 750, 550], outline='black', width=3)
    
    # Draw furniture
    draw.rectangle([100, 200, 300, 400], fill='brown')  # Table
    draw.rectangle([120, 150, 280, 200], fill='brown')  # Table top
    
    draw.rectangle([400, 200, 500, 500], fill='tan')  # Bookshelf
    draw.rectangle([420, 220, 480, 250], fill='red')  # Book 1
    draw.rectangle([420, 260, 480, 290], fill='blue')  # Book 2
    draw.rectangle([420, 300, 480, 330], fill='green')  # Book 3
    
    draw.rectangle([600, 300, 700, 500], fill='gray')  # Chair
    draw.rectangle([620, 280, 680, 300], fill='gray')  # Chair back
    
    # Draw window
    draw.rectangle([650, 100, 750, 200], fill='lightblue')
    draw.line([700, 100, 700, 200], fill='black', width=2)
    draw.line([650, 150, 750, 150], fill='black', width=2)
    
    img.save('examples/sample_images/indoor_scene.jpg')


def create_nature_scene():
    """Create a nature scene with animals and trees."""
    img = Image.new('RGB', (800, 600), color='lightgreen')
    draw = ImageDraw.Draw(img)
    
    # Draw ground
    draw.rectangle([0, 400, 800, 600], fill='brown')
    
    # Draw trees
    draw.rectangle([100, 300, 120, 400], fill='brown')  # Tree trunk 1
    draw.ellipse([50, 200, 170, 320], fill='darkgreen')  # Tree leaves 1
    
    draw.rectangle([300, 250, 320, 400], fill='brown')  # Tree trunk 2
    draw.ellipse([250, 150, 370, 270], fill='darkgreen')  # Tree leaves 2
    
    draw.rectangle([500, 280, 520, 400], fill='brown')  # Tree trunk 3
    draw.ellipse([450, 180, 570, 300], fill='darkgreen')  # Tree leaves 3
    
    # Draw animals
    draw.ellipse([200, 450, 250, 500], fill='brown')  # Rabbit body
    draw.ellipse([210, 430, 220, 450], fill='brown')  # Rabbit head
    draw.ellipse([205, 435, 210, 440], fill='brown')  # Rabbit ear 1
    draw.ellipse([220, 435, 225, 440], fill='brown')  # Rabbit ear 2
    
    draw.ellipse([400, 450, 450, 500], fill='orange')  # Fox body
    draw.ellipse([410, 430, 440, 450], fill='orange')  # Fox head
    draw.ellipse([405, 425, 415, 435], fill='orange')  # Fox ear 1
    draw.ellipse([435, 425, 445, 435], fill='orange')  # Fox ear 2
    
    # Draw birds
    draw.ellipse([150, 100, 170, 120], fill='black')  # Bird 1
    draw.ellipse([350, 80, 370, 100], fill='black')  # Bird 2
    draw.ellipse([550, 120, 570, 140], fill='black')  # Bird 3
    
    img.save('examples/sample_images/nature_scene.jpg')


def create_abstract_shapes():
    """Create abstract shapes for testing annotation tools."""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw various shapes
    draw.rectangle([100, 100, 200, 200], fill='red')  # Square
    draw.ellipse([250, 100, 350, 200], fill='blue')  # Circle
    draw.polygon([(400, 100), (450, 200), (350, 200)], fill='green')  # Triangle
    draw.rectangle([500, 100, 600, 150], fill='yellow')  # Rectangle
    
    # Draw overlapping shapes
    draw.ellipse([150, 300, 250, 400], fill='purple')
    draw.rectangle([200, 350, 300, 450], fill='orange')
    
    # Draw complex shapes
    draw.ellipse([400, 300, 500, 400], fill='cyan')
    draw.rectangle([450, 250, 550, 350], fill='magenta')
    
    # Draw small objects
    draw.ellipse([100, 500, 120, 520], fill='red')
    draw.ellipse([150, 500, 170, 520], fill='blue')
    draw.ellipse([200, 500, 220, 520], fill='green')
    
    img.save('examples/sample_images/abstract_shapes.jpg')


if __name__ == "__main__":
    create_sample_images()
