import time
import os
import functools  # Add this import at the top of the file
import logging


def log_execution_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start timing
        result = func(*args, **kwargs)  # Call the original function
        execution_time = time.time() - start_time  # Calculate execution time
        logging.debug(
            f"Execution time for {func.__name__}: {execution_time:.4f} seconds"
        )  # Log the execution time
        return result

    return wrapper


def list_blob_files(directory):
    try:
        # List all files in the given directory
        files = os.listdir(directory)

        # Filter files that contain "blob" in their name and are files (not directories)
        # blob_files = [
        #     file
        #     for file in files
        #     if "blob" in file and os.path.isfile(os.path.join(directory, file))
        # ]

        # # Print the list of files with "blob"
        # if blob_files:
        #     print(f"Files containing 'blob' in '{directory}':")
        #     for blob_file in blob_files:
        #         print(blob_file)
        # else:
        #     print(f"No files containing 'blob' found in '{directory}'.")
        return [f for f in files]

    except FileNotFoundError:
        print(f"The directory '{directory}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
