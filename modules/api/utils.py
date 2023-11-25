import numpy as np
import cv2
import tifffile as tif
from io import BytesIO
from PIL import Image
import os

def read_image_from_s3(session, bucketname, filename, region_name='us-east-1'):

    """Load image file from s3.

    Parameters
    ----------
    bucketname: string
        Bucket name
    filename : string
        Path in s3

    Returns
    -------
    np array
        Image array
    """
    s3 = session.resource('s3', region_name=region_name)
    bucket = s3.Bucket(bucketname)
    object = bucket.Object(filename)
    response = object.get()
    file_stream = response['Body']
    im = Image.open(file_stream)
    return im

def divide_and_save_from_memory(image, output_dir, file_name, patch_size=512):
    ext = file_name.split(".")[-1]

    # Get the image dimensions
    height, width = image.shape[:2]

    # Calculate the number of patches in each dimension
    num_patches_height = height // patch_size
    num_patches_width = width // patch_size

    # Iterate through patches and save them
    for i in range(num_patches_height):
        for j in range(num_patches_width):
            # Extract the patch
            patch = image[i * patch_size: (i + 1) * patch_size, j * patch_size: (j + 1) * patch_size]

            # Save the patch
            patch_file_path = os.path.join(output_dir, f"{i}_{j}.png")
            if ext == "tif":
                cv2.imwrite(patch_file_path, cv2.cvtColor(patch, cv2.COLOR_RGB2BGR))
            else:
                cv2.imwrite(patch_file_path, patch)

# Write image back to bucket
def write_image_to_s3(session, pil_image, bucketname, filename, region_name='us-east-1'):
    """Write an image array into S3 bucket

    Parameters
    ----------
    bucketname: string
        Bucket name
    filename : string
        Path in s3
    pil_image: Image
        pil image to be written

    Returns
    -------
    None
    """
    s3 = session.resource('s3', region_name=region_name)
    bucket = s3.Bucket(bucketname)
    object = bucket.Object(filename)
    file_stream = BytesIO()
    pil_image.save(file_stream, format='png')
    object.put(Body=file_stream.getvalue())

def recombine_images(input_dir, output_file_name, output_dir="", session=None):
    def rows_columns(file_names):
        max_i = max_j = -1  # Initialize max_i and max_j with negative infinity

        for file_name in file_names:
            i = file_name.split("/")[-1].split("_")[0][-1]
            j = file_name.split("/")[-1].split("_")[1][0]

            # Update max_i and max_j if necessary
            max_i = max(max_i, int(i))
            max_j = max(max_j, int(j))
        return max_i, max_j

    file_names = os.listdir(input_dir)
    rows, columns = rows_columns(file_names)
    
#     first_patch = cv2.imread(f"{input_dir}/{0}_{0}.png")
    first_patch = cv2.imread(f"{input_dir}/{0}_{0}-0000.png")
    image_height, image_width = first_patch.shape[:2]

    # Create a blank canvas for the final image
    final_image = Image.new('RGB', (columns * image_width, rows * image_height))

    for row in range(rows):
        for col in range(columns):
            # Open each individual image
#             image_path = f"{input_dir}/{row}_{col}.png"
            image_path = f"{input_dir}/{row}_{col}-0000.png"
            img = Image.open(image_path)

            # Calculate the position to paste the image on the canvas
            x_position = col * image_width
            y_position = row * image_height

            # Paste the image onto the final canvas
            final_image.paste(img, (x_position, y_position))
    output_path = f"{output_dir}/{output_file_name}.png"
    final_image.save(output_path)

    if session is not None:
        write_image_to_s3(session, final_image, 'satupscale', "final_image.png", )