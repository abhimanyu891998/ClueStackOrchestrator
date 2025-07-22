def read_file(file_path: str) -> str:
    """
    Read content of a file and return it as string.

    Args:
        file_path: Path to the file to read

    Returns:
        String containing the file content

    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there is an error reading the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")
