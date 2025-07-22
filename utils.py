from langchain_core.messages import convert_to_messages

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


def pretty_print_message(message, indent=False):
    """Pretty print a agent/LLM message"""
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return
    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)

def pretty_print_messages(chunk, last_message=False):
    # (assume convert_to_messages is imported)
    messages = convert_to_messages(chunk["messages"])
    if last_message:
        messages = messages[-1:]
    for m in messages:
        pretty_print_message(m)
        print()
