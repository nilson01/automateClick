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

def load_image(image_path):
    """Loads an image from the provided path."""
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def search_and_click(image_path, label, method=cv2.TM_CCOEFF_NORMED, threshold=0.9):
    """Searches for an image on the screen and clicks it. 
    This function will keep searching until the image is found and clicked."""
    
    while True:
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)

        # Get screen size
        screen_width, screen_height = pyautogui.size()
        screenshot_height, screenshot_width = screen_gray.shape[:2]

        scale_x = screen_width / screenshot_width
        scale_y = screen_height / screenshot_height

        # Load the template image
        template = load_image(image_path)

        # Perform template matching
        result = cv2.matchTemplate(screen_gray, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            x, y = max_loc
            x_center = int(x + template.shape[1] // 2)
            y_center = int(y + template.shape[0] // 2)
            scaled_x = int(x_center * scale_x)
            scaled_y = int(y_center * scale_y)

            # Click on the center of the matched template
            pyautogui.click(scaled_x, scaled_y)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Print and log the click event
            print(f"{timestamp} | Step: {label} | Clicked at ({scaled_x}, {scaled_y}) | Probability: {max_val:.2f}")
            logging.info(f"Timestamp: {timestamp}, Step: {label}, Coordinates: ({scaled_x}, {scaled_y}), Probability: {max_val:.2f}")
            time.sleep(1)  # Short delay to let the click take effect

            return
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {label} not found. Retrying...")
            time.sleep(1)  # Wait for 1 second before retrying

def double_click_write_button(write_button_path):
    """Click the Write button twice to ensure it is fully clicked."""
    print("Clicking Write button twice for confirmation...")
    logging.info("Clicking Write button twice for confirmation...")

    for attempt in range(1, 2):  # Click Write button k times, k = 1
        search_and_click(write_button_path, label=f"Write Button (attempt {attempt})", threshold=0.95)
        # time.sleep(1)  # Small delay between clicks to avoid issues

    print("Write button clicked twice, proceeding to Confirm step...")
    logging.info("Write button clicked twice, proceeding to Confirm step...")

def metamask_process(metamask_icon_path, speedup_button_path, submit_button_path):
    """Handles the MetaMask process sequentially, without skipping any step."""
    print("Starting MetaMask process...")
    logging.info("Starting MetaMask process...")

    # Step 1: Click MetaMask Icon
    search_and_click(metamask_icon_path, label="MetaMask Icon", threshold=0.8)

    # Step 2: Click Speed Up button
    search_and_click(speedup_button_path, label="Speed Up", threshold=0.8)

    # Step 3: Click Submit button
    search_and_click(submit_button_path, label="Submit", threshold=0.8)

    print("MetaMask process complete. Returning to Write button search.")
    logging.info("MetaMask process complete.")

def search_and_run(images, metamask_icon_path, speedup_button_path, submit_button_path, threshold=0.9, duration=60):
    """Main loop that searches for images, clicks them, and handles the MetaMask process sequentially."""
    method = cv2.TM_CCOEFF_NORMED

    # Timer for running the loop
    start_time = time.time()

    # Track how many rounds have been completed
    first_round_complete = False

    while time.time() - start_time < duration:
        # Step 1: Look for the Write button (mandatory)
        print("Looking for Write Button...")
        search_and_click(images['write_button'], label="Write Button", threshold=0.95)

        # Step 1.5: If it's the first round, just click once; for subsequent rounds, click twice
        if first_round_complete:
            double_click_write_button(images['write_button'])
        else:
            print("First round: single click for Write button")
            logging.info("First round: single click for Write button")

        # Step 2: Look for the Confirm button (mandatory)
        print("Looking for Confirm Button...")
        search_and_click(images['confirm_button'], label="Confirm Button", threshold=0.9)

        # Step 3: Perform the MetaMask process (mandatory steps)
        metamask_process(metamask_icon_path, speedup_button_path, submit_button_path)

        # Mark first round as complete after going through the whole sequence
        if not first_round_complete:
            first_round_complete = True
            print("First round completed, next round will involve double-click for Write button.")
            logging.info("First round completed, next round will involve double-click for Write button.")

        # After finishing MetaMask process, the loop restarts by looking for the Write button again.
        # time.sleep(1)  # Short delay before the next iteration

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

    # Paths to image templates
    image_paths = {
        'write_button': r"source/write_button.png",
        'confirm_button': r"source/confirm_button.png"
    }
    metamask_icon_path = r"source/metamask.png"
    speedup_button_path = r"source/speedup_button.png"
    submit_button_path = r"source/Submit_button.png"

    # Call the function with the list of image paths and the determined duration
    search_and_run(image_paths, metamask_icon_path, speedup_button_path, submit_button_path, threshold=0.9, duration=duration)

# Entry point of the script
if __name__ == "__main__":
    # You can pass 'testing' or 'production' mode as an argument
    mode = input("Enter mode (testing/production): ").strip().lower()
    main(mode)
