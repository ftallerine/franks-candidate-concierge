from pathlib import Path
import shutil

def setup_image():
    # Create the images directory if it doesn't exist
    image_dir = Path(__file__).parent / "static" / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to the headshot
    headshot_path = image_dir / "frank_headshot.jpg"
    
    if not headshot_path.exists():
        print(f"Please place your headshot image at: {headshot_path}")
        print("The image should be named 'frank_headshot.jpg'")

if __name__ == "__main__":
    setup_image() 