import os
from PIL import Image
import re

def analyze_images():
    image_dir = 'images'
    try:
        files = sorted(os.listdir(image_dir))
    except FileNotFoundError:
        print(f"Directory '{image_dir}' not found.")
        return

    brightness_data = []

    for filename in files:
        if not filename.endswith('.jpg'):
            continue

        filepath = os.path.join(image_dir, filename)

        # Extract timestamp
        # frame_000_0.0s.jpg
        match = re.search(r'_(\d+\.\d+)s\.jpg', filename)
        if match:
            timestamp = float(match.group(1))
        else:
            continue

        try:
            img = Image.open(filepath).convert('L')
            width, height = img.size

            # Crop center 50x50
            crop_size = 50
            left = (width - crop_size) / 2
            top = (height - crop_size) / 2
            right = (width + crop_size) / 2
            bottom = (height + crop_size) / 2

            cropped = img.crop((left, top, right, bottom))

            pixels = list(cropped.getdata())
            avg_brightness = sum(pixels) / len(pixels)

            brightness_data.append({'time': timestamp, 'brightness': avg_brightness})
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    events = []
    trend = None # 'increasing', 'decreasing', 'stable'
    THRESHOLD = 12 # Threshold to ignore noise

    # Prepare table data
    table_rows = []

    # First row (no delta)
    if brightness_data:
        table_rows.append({
            'time': brightness_data[0]['time'],
            'brightness': brightness_data[0]['brightness'],
            'delta': 0.0,
            'classification': ''
        })

    for i in range(1, len(brightness_data)):
        curr = brightness_data[i]
        prev = brightness_data[i-1]

        diff = curr['brightness'] - prev['brightness']
        classification = ''

        if diff > THRESHOLD:
             current_trend = 'increasing'
        elif diff < -THRESHOLD:
             current_trend = 'decreasing'
        else:
             current_trend = 'stable'

        if current_trend == 'increasing':
            if trend != 'increasing':
                classification = 'ON'
            trend = 'increasing'
        elif current_trend == 'decreasing':
            if trend != 'decreasing':
                classification = 'OFF'
            trend = 'decreasing'
        else:
            trend = 'stable'

        table_rows.append({
            'time': curr['time'],
            'brightness': curr['brightness'],
            'delta': diff,
            'classification': classification
        })

        if classification:
            events.append(f"{curr['time']}s: {classification}")

    # Print events
    for event in events:
        print(event)

    # Save events to file
    with open('timelog.txt', 'w') as f:
        for event in events:
            f.write(event + '\n')

    # Print Markdown Table
    print("\n| Time | Brightness | Delta | Classification |")
    print("|---|---|---|---|")
    for row in table_rows:
        print(f"| {row['time']:.1f}s | {row['brightness']:.2f} | {row['delta']:.2f} | {row['classification']} |")

if __name__ == "__main__":
    analyze_images()
