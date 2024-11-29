from db.db import createUser, check_user_pwd, get_mailbox, create_mailbox, search_mailbox, receive_message
from errors.nuerrors import NuMailError
from server.message.Attachment import Attachment

try:
    print(createUser(
        user_name="micah",
        display_name="Micah Baumann",
        password="12345",
        isAdmin=True,
        first_name="Micah",
        last_name="Baumann"
    ))
except NuMailError as e:
    print(e)
except Exception as e:
    print(e)

try:
    print(check_user_pwd(
        user_name="micah",
        password="123456"
    ))
except NuMailError as e:
    print(e)
except Exception as e:
    print(e)

try:
    print(create_mailbox(
        user_name="micah",
        mb_name="micah",
        mb_send=True,
        mb_receive=True
    ))
except NuMailError as e:
    print(e)
except Exception as e:
    print(e)

try:
    print(get_mailbox(
        user_name="micah",
        mb_name="micah"
    ))
except NuMailError as e:
    print(e)
except Exception as e:
    print(e)

try:
    print(search_mailbox(
        mb_name="micah"
    ))
except NuMailError as e:
    print(e)
except Exception as e:
    print(e)

try:
    print(receive_message(
        from_addr = "micah@numail.local",
        to_addr = "micah@other.local",
        msgt = 0,
        data = "fdasadfasdjkl;afsd",
        readConfirm = False
    ))
except NuMailError as e:
    print("NuMail Error:")
    print(e)
except Exception as e:
    print("Exception:")
    print(e)




# import base64
# def safe_b64decode(b64_string):
#         padding_needed = len(b64_string) % 4
#         if padding_needed:
#             b64_string += '=' * (4 - padding_needed)
#         return base64.b64decode(b64_string)
# def create_mime_attachment(file_path, mime_type="application/octet-stream"):
#     # Extract file name
#     file_name = file_path.split("/")[-1]

#     # Read and encode the file in base64
#     with open(file_path, "rb") as file:
#         file_content = base64.b64encode(file.read().strip()).decode("utf-8")
    
#     with open("f_output.jpeg", "w") as file:
#         file.write(Attachment.safe_b64decode(file_content).decode("utf-8"))

#     # Create MIME headers
#     mime_headers = f"""\r\nContent-Type: {mime_type}; name="{file_name}"\r\nContent-Disposition: attachment; filename="{file_name}"\r\nContent-Transfer-Encoding: base64\r\n\r\n"""
#     # Combine headers and encoded content
#     mime_message = mime_headers + file_content
#     return mime_message

# # Example usage
# file_path = "test_file.jpeg"  # Replace with your file path
# mime_data = create_mime_attachment(file_path, "image/jpeg")

# # Print the MIME-formatted data
# with open("mime_output.txt", "w") as file:
#     file.write(mime_data)

# print(list(Attachment(data=mime_data)))