import os
from PIL import Image

# Configuration
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, 'image_input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'image_output')
COLOR_MAIN = "#0f777c"
OPACITY = 0.4

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def process_images():
    # Ensure directories exist
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"Created input directory at: {INPUT_DIR}")
        print("Please place images in the input directory and run the script again.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory at: {OUTPUT_DIR}")

    # List images
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(valid_extensions)]
    
    if not files:
        print(f"No images found in {INPUT_DIR}.")
        return

    print(f"Found {len(files)} images. Processing with overlay {COLOR_MAIN} at {int(OPACITY*100)}% opacity...")

    overlay_rgb = hex_to_rgb(COLOR_MAIN)
    # Alpha for the overlay layer (0-255)
    overlay_alpha = int(255 * OPACITY)
    # The overlay color tuple including alpha
    overlay_color = overlay_rgb + (overlay_alpha,)

    processed_count = 0
    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        try:
            with Image.open(input_path) as img:
                # Convert to RGBA to allow alpha composition
                img_rgba = img.convert("RGBA")
                
                # Create a solid color layer of the same size
                overlay = Image.new('RGBA', img_rgba.size, overlay_color)
                
                # Composite the overlay onto the image
                # The overlay is put ON TOP of the image
                combined = Image.alpha_composite(img_rgba, overlay)
                
                # Save output
                # If original was JPG, convert back to RGB; otherwise keep RGBA (e.g. PNG)
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    final_img = combined.convert("RGB")
                    final_img.save(output_path, quality=95)
                else:
                    combined.save(output_path)
                
                print(f"[{processed_count+1}/{len(files)}] Processed: {filename}")
                processed_count += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"\nDone! Processed {processed_count} images. Results in {OUTPUT_DIR}")

if __name__ == "__main__":
    process_images()
