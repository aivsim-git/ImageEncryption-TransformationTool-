import numpy as np
from PIL import Image
import cv2
import os

# ------------------------------
# Image Handling
# ------------------------------

def load_image(path, as_gray=False):
    """Load an image from the given path."""
    try:
        if as_gray:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            return img, "L"
        else:
            img = Image.open(path)
            return np.array(img), img.mode
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None, None

def save_image(array, mode, path):
    """Save an image array to disk."""
    try:
        if mode == "L":
            cv2.imwrite(path, array)
        else:
            img = Image.fromarray(array.astype('uint8'), mode)
            img.save(path)
        print(f"✅ Image saved as: {path}")
    except Exception as e:
        print(f"❌ Error saving image: {e}")

# ------------------------------
# Pixel-Level Encryption
# ------------------------------

def encrypt_pixels(img_array, key):
    """Encrypt image using XOR and flip."""
    return np.flipud(img_array) ^ key

def decrypt_pixels(img_array, key):
    """Decrypt image by reversing encryption steps."""
    return np.flipud(img_array ^ key)

# ------------------------------
# Fourier Transform Encryption
# ------------------------------

def encrypt_fourier(img_array, spectrum_file):
    """Encrypt by applying FFT and saving the spectrum."""
    f = np.fft.fft2(img_array)
    np.save(spectrum_file, f)  # Save complex data
    magnitude = 20 * np.log(np.abs(np.fft.fftshift(f)) + 1)
    return magnitude.astype(np.uint8)

def decrypt_fourier(spectrum_file):
    """Decrypt by applying inverse FFT from saved spectrum."""
    try:
        f = np.load(spectrum_file)
        img_back = np.fft.ifft2(f)
        img_back = np.abs(img_back)
        return np.uint8(img_back)
    except Exception as e:
        print(f"❌ Error decrypting Fourier data: {e}")
        return None

# ------------------------------
# Laplacian (One-Way Filter)
# ------------------------------

def apply_laplacian(img_array):
    """Apply Laplacian edge detection."""
    lap = cv2.Laplacian(img_array, cv2.CV_64F)
    abs_lap = np.absolute(lap)
    return np.uint8(abs_lap)

# ------------------------------
# Input Validation
# ------------------------------

def get_int_input(prompt, min_val=0, max_val=255):
    """Prompt the user for a valid integer in range."""
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Enter a valid integer.")

# ------------------------------
# Main Interface
# ------------------------------

def main():
    print("\n=== 🔐 Image Encryption Tool ===")
    print("1. Pixel-based Encryption/Decryption")
    print("2. Fourier Transform Encryption/Decryption")
    print("3. Laplacian Transform (edge detection only)")

    choice = input("Choose method (1/2/3): ").strip()

    if choice == "1":
        operation = input("Encrypt (e) or Decrypt (d)? ").strip().lower()
        path = input("Enter image path: ").strip()
        key = get_int_input("Enter encryption key (0-255): ")
        output = input("Output image filename: ").strip()

        img_array, mode = load_image(path)
        if img_array is None: return

        result = encrypt_pixels(img_array, key) if operation == 'e' else decrypt_pixels(img_array, key)
        save_image(result, mode, output)

    elif choice == "2":
        operation = input("Encrypt (e) or Decrypt (d)? ").strip().lower()

        if operation == 'e':
            path = input("Enter grayscale image path: ").strip()
            spectrum_file = input("Enter path to save spectrum data (e.g., spectrum.npy): ").strip()
            output = input("Output (magnitude image) filename: ").strip()

            img_array, mode = load_image(path, as_gray=True)
            if img_array is None: return

            result = encrypt_fourier(img_array, spectrum_file)
            save_image(result, "L", output)

        elif operation == 'd':
            spectrum_file = input("Enter .npy spectrum file path: ").strip()
            output = input("Output decrypted image filename: ").strip()

            result = decrypt_fourier(spectrum_file)
            if result is not None:
                save_image(result, "L", output)

        else:
            print("❌ Invalid operation. Use 'e' or 'd'.")

    elif choice == "3":
        path = input("Enter image path: ").strip()
        output = input("Output image filename: ").strip()

        img_array, mode = load_image(path, as_gray=True)
        if img_array is None: return

        lap = apply_laplacian(img_array)
        save_image(lap, "L", output)

    else:
        print("❌ Invalid choice. Please enter 1, 2, or 3.")

# ------------------------------
if __name__ == "__main__":
    main()
1