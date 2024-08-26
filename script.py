import os
import io
from PIL import Image
import base64
from openai import OpenAI

"""Find the most recently added PNG screenshot"""
def find_most_recent_screenshot(directory):
    png_files = [
        os.path.join(directory, filename) for filename in os.listdir(directory)
        if filename.endswith('.png')
    ]

    if not png_files:
        print("No PNG files found in the directory.")
        return None

    most_recent_png = max(png_files, key=os.path.getmtime)
    print(f"Latest PNG found: {most_recent_png}")
    return most_recent_png


"""Check if a file has been processed before"""
def has_been_processed(filename, processed_log_file):
    if os.path.isfile(processed_log_file):
        with open(processed_log_file, 'r') as log_file:
            if filename in log_file.read():
                return True
    return False
    

"""Mark a file as processed by logging the name"""
def mark_as_processed(filename, processed_log_file):
    with open(processed_log_file, "a") as log_file:
        log_file.write(filename + "\n")
    print(f"Logged file: {filename}")


"""Rename the screenshot based on the description"""
def rename_screenhot(screenshot_path, description):
    directory, filename = os.path.split(screenshot_path)
    new_filename = "_".join(description.split()) + ".png"
    new_file_path = os.path.join(directory, new_filename)
    os.rename(screenshot_path, new_file_path)
    return new_file_path


"""Format the image to 512 res and get the base 64 encoding"""
def format_screenhot(most_recent_screenshot):
    with Image.open(most_recent_screenshot) as img:
        img_res = 512
        width, height = img.size
        resized_img = img.resize(
            (img_res, int(img_res * height / width)), 
            Image.LANCZOS
        )
        buffered = io.BytesIO()
        resized_img.save(buffered, format="PNG")
        
        base64_img = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return base64_img


"""Analyze the image using GPT-4 Vision and get a description"""
def get_description_for_screenhot(base64_img):
    open_ai_key = ''
    client = OpenAI(api_key=open_ai_key)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "This is a screenshot I took on my screen."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_img}",
                        },
                    },
                    {
                        "type": "text", 
                        "text": "Give me with a concise, descriptive file name for this image, using up to 6 words separated by spaces. Make sure to exclude the file extension."
                    }
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def main():
    screenshots_folder = "/Users/sahlbakshi/Desktop"
    processed_log_file = "/Users/sahlbakshi/Developer/smart-snap/processed.log"

    most_recent_screenshot = find_most_recent_screenshot(screenshots_folder)

    if most_recent_screenshot and not has_been_processed(most_recent_screenshot, processed_log_file):
        description = get_description_for_screenhot(format_screenhot(most_recent_screenshot))
        new_screenshot_path = rename_screenhot(most_recent_screenshot, description)
        mark_as_processed(new_screenshot_path, processed_log_file)
    else:
        print("No new screenshots to process or already processed.")

if __name__ == "__main__":
    main()
    