import cv2
import numpy as np
import pyautogui
import time
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='clicker.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

# Function to search for images on the screen and click on them if found
def search_and_click(images, threshold=0.8, click_delay=0.01, duration=60):
    # Set the template matching method
    method = cv2.TM_CCOEFF_NORMED

    # Get the actual screen resolution
    screen_width, screen_height = pyautogui.size()

    # Timer for running the loop
    start_time = time.time()

    while time.time() - start_time < duration:
        # Capture the screen image using pyautogui (faster than PIL/ImageGrab)
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)

        # Get the screenshot dimensions (they could differ from the screen size)
        screenshot_height, screenshot_width = screen_gray.shape[:2]

        # Calculate scaling factors if the screenshot size differs from the screen size
        scale_x = screen_width / screenshot_width
        scale_y = screen_height / screenshot_height

        # Iterate through each image in the provided list of images
        for image_path in images:
            if not os.path.exists(image_path):
                logging.error(f"Image not found at '{image_path}'")
                continue  # Skip to the next image if the file doesn't exist

            # Load the template image from the disk
            template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

            # Perform template matching
            result = cv2.matchTemplate(screen_gray, template, method)

            # Get the locations where matches are above the specified threshold
            loc = np.where(result >= threshold)

            # Click on the matched locations
            if loc[0].size > 0:
                for pt in zip(*loc[::-1]):
                    # Calculate the center of the matched template
                    x, y = pt[0] + template.shape[1] // 2, pt[1] + template.shape[0] // 2

                    # Scale the coordinates to match the actual screen resolution
                    scaled_x = int(x * scale_x)
                    scaled_y = int(y * scale_y)

                    # Get the current timestamp
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Click on the center of the matched template
                    pyautogui.click(scaled_x, scaled_y)

                    # Get the maximum probability from the match result
                    max_probability = result[pt[1], pt[0]]

                    # Print in reverse order: timestamp, coordinates, probability
                    print(f"{timestamp} | Coordinates: ({scaled_x}, {scaled_y}) | Probability: {max_probability:.2f}")

                    # Log the same information
                    logging.info(f"Timestamp: {timestamp}, Coordinates: ({scaled_x}, {scaled_y}), Probability: {max_probability:.2f}")

                    # Delay between clicks
                    time.sleep(click_delay)

# Main function to execute the script
def main(mode):
    # Determine the duration based on mode
    if mode == 'testing' or mode == '0':
        duration = 60  # 1 minute in seconds
        print("Running in testing mode for 1 minute.")
    elif mode == 'production' or mode == '1':
        duration = 60 * 1  # 1 hour in seconds -> 60x60
        print("Running in production mode for 1 hour.")
    else:
        print("Invalid mode. Please use 'testing' or 'production'.")
        return

    # List of image paths to search for on the screen (place the paths to your actual images)
    image_paths = [
        r"source/write_button.png",
        r"source/confirm_button.png",
        # Add more image paths as needed
    ]

    # Call the function with the list of image paths and the determined duration
    search_and_click(image_paths, threshold=0.9, duration=duration)


# Entry point of the script
if __name__ == "__main__":
    # You can pass 'testing' or 'production' mode as an argument
    mode = input("Enter mode (testing/production): ").strip().lower()
    main(mode)
