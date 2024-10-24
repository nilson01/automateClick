import cv2
import numpy as np
import pyautogui
import time
import os
import logging
from datetime import datetime
import platform

# Set up logging
logging.basicConfig(filename='clicker.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

def load_image(image_path):
    """Loads an image from the provided path."""
    if os.path.exists(image_path):
        return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        logging.error(f"Image not found at '{image_path}'")
        return None

def search_and_click(images, threshold=0.9, click_delay=0.01, duration=60):
    """Searches for images on the screen and clicks on them."""
    
    # Set the template matching method
    method = cv2.TM_CCOEFF_NORMED

    # Get actual screen resolution
    screen_width, screen_height = pyautogui.size()

    # Timer to run the loop
    start_time = time.time()

    while time.time() - start_time < duration: 
        
        # Capture screen image using pyautogui
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)

        # Get screenshot dimensions
        screenshot_height, screenshot_width = screen_gray.shape[:2]

        # Calculate scaling factors if the screenshot size differs from the screen size
        scale_x = screen_width / screenshot_width
        scale_y = screen_height / screenshot_height

        # Iterate through the provided images and perform template matching
        for image_path in images:
            template = load_image(image_path)
            if template is None:
                continue

            result = cv2.matchTemplate(screen_gray, template, method)
            loc = np.where(result >= threshold)

            if loc[0].size > 0:
                for pt in zip(*loc[::-1]):
                    x, y = pt[0] + template.shape[1] // 2, pt[1] + template.shape[0] // 2
                    scaled_x, scaled_y = int(x * scale_x), int(y * scale_y)
                    max_probability = result[pt[1], pt[0]]

                    # Click on the center of the matched template
                    pyautogui.click(scaled_x, scaled_y)

                    # Get the current timestamp
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Print and log the click details
                    print(f"{timestamp} | Coordinates: ({scaled_x}, {scaled_y}) | Probability: {max_probability:.2f}")
                    logging.info(f"Timestamp: {timestamp}, Coordinates: ({scaled_x}, {scaled_y}), Probability: {max_probability:.2f}")

                    # Delay between clicks
                    # time.sleep(click_delay)
        time.sleep(click_delay)

def get_image_paths():
    """Get image paths based on the user's operating system."""
    
    # Get current OS
    system = platform.system()

    # Get the base path for images
    base_path = os.path.join(os.getcwd(), "source")

    # Set up image paths depending on the OS
    if system == "Windows":
        print("Running on Windows")
        write_button_path = os.path.join(base_path, "write_button.png")
        confirm_button_path = os.path.join(base_path, "confirm_button.png")
    else:
        print(f"Running on {system}")
        write_button_path = os.path.join(base_path, "write_button.png")
        confirm_button_path = os.path.join(base_path, "confirm_button.png")

    return [write_button_path, confirm_button_path]

def main():
    """Main function to run the script based on mode (testing or production)."""
    
    mode = input("Enter mode (testing/production): ").strip().lower()
    
    if mode == 'testing' or mode == '0':
        duration = 60  # 1 minute
        print("Running in testing mode for 1 minute.")
    elif mode == 'production' or mode == '1':
        duration = 60 * 60 * 5  # 1 hour
        print("Running in production mode for 1 hour.")
    else:
        print("Invalid mode. Please use 'testing' or 'production'.")
        return

    # Get the image paths based on OS
    image_paths = get_image_paths()

    # Start the automation process
    search_and_click(image_paths, threshold=0.9, click_delay=20, duration=duration)

if __name__ == "__main__":
    main()
