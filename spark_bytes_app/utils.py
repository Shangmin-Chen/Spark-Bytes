import qrcode
from io import BytesIO
import base64

def generate_qr_code(data):
    """
    Generates a QR code for the provided data and returns it as a base64-encoded string.

    Args:
        data (str): The data to encode in the QR code, such as event details or user-specific information.

    Returns:
        str: A base64-encoded string representation of the QR code image.

    Workflow:
        1. Create a QRCode object with specified parameters (version, error correction, box size, border).
        2. Add the input data to the QRCode object.
        3. Generate the QR code as an image.
        4. Save the image to a BytesIO buffer in PNG format.
        5. Encode the image data to a base64 string and return it.

    Example:
        qr_code = generate_qr_code("https://Spark-Bytes.com/event")
        # `qr_code` contains a base64-encoded PNG image of the QR code.
    """
    # Create a QRCode object with specified parameters
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code (1 is the smallest).
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level (L: ~7% recovery).
        box_size=10,  # Size of each box in the QR code grid.
        border=4,  # Border size in boxes around the QR code.
    )
    qr.add_data(data)  # Add the input data to the QR code
    qr.make(fit=True)  # Adjust the QR code size to fit the data

    # Render the QR code as an image
    img = qr.make_image(fill_color="black", back_color="white")  # Customize QR code colors
    buffered = BytesIO()  # Create a BytesIO buffer to store the image in memory
    img.save(buffered, format="PNG")  # Save the image in PNG format to the buffer

    # Convert the image data to a base64-encoded string
    return base64.b64encode(buffered.getvalue()).decode("utf-8")