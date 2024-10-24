import cv2
import pyautogui
import numpy as np
import time
import os
from datetime import datetime
from PIL import ImageGrab

def load_image(image_path):
    """Loads an image from the provided path."""
    return cv2.imread(image_path)

def capture_screen_to_file(file_name):
    """Captures a screenshot of the current screen and saves it as an image file."""
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)
    cv2.imwrite(file_name, screenshot_rgb)

def multi_scale_template_match(screen_image, template_image, threshold=0.8):
    """Performs multi-scale template matching to find the template on the screen image."""
    template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
    screen_gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)

    template_h, template_w = template_gray.shape[:2]
    
    best_match = None
    best_val = 0
    best_template_size = (template_w, template_h)
    
    # Loop over scales to handle different sizes of the button
    for scale in np.linspace(0.5, 1.5, 20):
        # Resize the template according to the scale
        resized_template = cv2.resize(template_gray, (int(template_w * scale), int(template_h * scale)))
        res = cv2.matchTemplate(screen_gray, resized_template, cv2.TM_CCOEFF_NORMED)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val > threshold and max_val > best_val:
            best_val = max_val
            best_match = max_loc
            # Resize dimensions according to the matched scale
            best_template_size = (int(template_w * scale), int(template_h * scale))
    
    return best_match, best_template_size, best_val

def annotate_and_save_image(screen_image, match_location, template_size, match_probability, folder_path, button_name):
    """Annotates the matched location by drawing a rectangle and adding the match probability and coordinates."""
    if match_location:
        x, y = match_location
        w, h = template_size
    
        # Draw a rectangle around the matched area
        cv2.rectangle(screen_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Annotate with probability and coordinates
        text = f"Prob: {match_probability:.2f}, Coord: ({x}, {y})"
        cv2.putText(screen_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Generate the file path with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(folder_path, f'annotated_{button_name}_{timestamp}.png')

        # Save the annotated image
        cv2.imwrite(output_path, screen_image)
        print(f"Annotated image saved to {output_path}")
    else:
        print(f"No match found for {button_name}, so no annotation was done.")

def click_button_on_screen(template_image_path, button_name, folder_path, threshold=0.8):
    """Captures the screen, looks for the template, clicks on the button when found, and annotates the image."""
    template_image = load_image(template_image_path)

    # Get screen size
    screen_width, screen_height = pyautogui.size()

    while True:
        # Capture the current screen to a fixed file name (overwrite each time)
        capture_screen_to_file(f'test_{button_name}.png')

        # Load the captured screen image
        screen_image = load_image(f'test_{button_name}.png')
        
        # Get the screenshot dimensions
        screenshot_height, screenshot_width = screen_image.shape[:2]
        
        # Calculate the scaling factors between the screenshot and the screen
        scale_x = screen_width / screenshot_width
        scale_y = screen_height / screenshot_height
        
        # Find the button on the screen
        match_location, template_size, match_probability = multi_scale_template_match(screen_image, template_image, threshold)
        
        if match_location:
            # Calculate the center of the detected button
            x, y = match_location
            w, h = template_size
            center_x = x + w // 2
            center_y = y + h // 2

            # Adjust the coordinates based on the scaling factor
            adjusted_center_x = int(center_x * scale_x)
            adjusted_center_y = int(center_y * scale_y)

            # Simulate a click using PyAutoGUI at the center of the button
            pyautogui.click(adjusted_center_x, adjusted_center_y)
            print(f"{button_name} button clicked at coordinates: ({adjusted_center_x}, {adjusted_center_y}) with probability {match_probability:.2f}")

            # Annotate the screenshot with the match information
            annotate_and_save_image(screen_image, match_location, template_size, match_probability, folder_path, button_name)

            break  # Exit the loop after clicking

        else:
            print(f"{button_name} button not found, waiting and retrying...")
            time.sleep(1)  # Wait before trying again

def main():
    # Create the images folder if it doesn't exist
    folder_path = 'images'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Run the process for 1 hour
    start_time = time.time()
    duration = 60 * 1  # for 1 hour use -> 60x60

    while time.time() - start_time < duration:
        # Path to the "Write" button template image
        write_button_template = 'write_button.png'

        # Find and click the "Write" button, save annotated image
        click_button_on_screen(write_button_template, 'Write', folder_path)

        time.sleep(2)  # Wait before trying again

        # Path to the "Confirm" button template image
        confirm_button_template = 'confirm_button.png'

        # After "Write" is clicked, find and click the "Confirm" button, save annotated image
        click_button_on_screen(confirm_button_template, 'Confirm', folder_path)

        # Optional: sleep for a short interval before repeating
        time.sleep(2)  # To avoid constant loop, you can adjust the sleep time

    print("1 hour process completed.")

if __name__ == '__main__':
    main()
