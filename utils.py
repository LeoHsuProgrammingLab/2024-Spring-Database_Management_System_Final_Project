def truncate_text_to_bytes(text, max_bytes=5000):
    # Split the text into words
    words = text.split()
    truncated_text = []
    current_size = 0

    for word in words:
        word_size = len(word.encode('utf-8')) + 1  # Include the space character
        if current_size + word_size <= max_bytes:
            truncated_text.append(word)
            current_size += word_size
        else:
            break

    return ' '.join(truncated_text)