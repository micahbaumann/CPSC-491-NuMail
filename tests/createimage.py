# import base64

# # Convert file to base64
# def file_to_base64(file_path):
#     with open(file_path, "rb") as file:
#         base64_encoded = base64.b64encode(file.read())
#         return base64_encoded.decode('utf-8')  # Convert bytes to string

# # Convert base64 back to file
# def base64_to_file(base64_str, output_path):
#     with open(output_path, "wb") as file:
#         file.write(base64.b64decode(base64_str))

# # Example usage
# input_file = "test_file.jpeg"   # Replace with your input file path
# output_file = "output.jpeg"   # Replace with your desired output file path

# # Convert the file to base64
# base64_data = file_to_base64(input_file)
# print(f"Base64 Encoded Data:\n{base64_data}")

# # Convert the base64 string back to a file
# base64_to_file(base64_data, output_file)
# print(f"File has been decoded to: {output_file}")





import base64

# Convert a file to Base64 and format it for an email attachment
def format_file_as_email_attachment(file_path, file_name):
    with open(file_path, "rb") as file:
        base64_encoded = base64.b64encode(file.read()).decode('utf-8')
    # Format for email attachment with \r\n line endings
    email_attachment = (
        f"Content-Disposition: attachment; filename=\"{file_name}\"\r\n"
        "Content-Transfer-Encoding: base64\r\n"
        "Content-Type: application/octet-stream\r\n\r\n"
        f"{base64_encoded}\r\n"
    )
    return email_attachment

# Save the formatted email attachment to a text file
def save_attachment_to_text_file(email_attachment, output_text_file):
    with open(output_text_file, "w") as file:
        file.write(email_attachment)

# Extract Base64 from email attachment and save back to a file
def extract_file_from_email_attachment(email_attachment, output_path):
    # Locate the start of the Base64 content (after the blank line)
    header_body_split = email_attachment.split("\r\n\r\n", 1)
    if len(header_body_split) != 2:
        raise ValueError("Invalid MIME format: Missing blank line separating headers and body.")
    base64_content = header_body_split[1]  # Content after headers
    with open(output_path, "wb") as file:
        file.write(base64.b64decode(base64_content))

# Example usage
input_file = "test_file.jpeg"        # Input file to encode
output_file = "output.jpeg"        # Output file to decode
output_text_file = "mime_output_2.txt"  # File to save the formatted email attachment

# Step 1: Convert file to email-formatted attachment
file_name = "test_file.jpeg"         # The name of the file as it appears in the email attachment
formatted_attachment = format_file_as_email_attachment(input_file, file_name)

# Step 2: Save the formatted attachment to a text file
save_attachment_to_text_file(formatted_attachment, output_text_file)
print(f"Formatted email attachment saved to: {output_text_file}")

# Step 3: Extract Base64 from email-formatted attachment and save to a file
extract_file_from_email_attachment(formatted_attachment, output_file)
print(f"File has been decoded back to: {output_file}")
