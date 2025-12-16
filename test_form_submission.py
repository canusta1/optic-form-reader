#!/usr/bin/env python3
"""Test form submission endpoint"""
import requests
import json
import os

# Test image path
test_image = os.path.join(os.path.dirname(__file__), 'backend', 'debug_images', 'IMG_0672.jpg')

if not os.path.exists(test_image):
    print(f"❌ Test image not found: {test_image}")
    exit(1)

print(f"📸 Test image: {test_image}")
print(f"📏 File size: {os.path.getsize(test_image)} bytes")

# Prepare form data
files = {
    'form_image': open(test_image, 'rb')
}
data = {
    'user_id': '1',
    'form_template': 'ygs'
}

url = 'http://127.0.0.1:5000/api/submit-form'

try:
    print(f"\n📡 Submitting to {url}...")
    response = requests.post(url, files=files, data=data, timeout=30)
    
    print(f"\n✅ Response Status: {response.status_code}")
    
    try:
        result = response.json()
        print("\n📋 Response JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except:
        print("\n📝 Response Text:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    files['form_image'].close()
