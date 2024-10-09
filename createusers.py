from db.db import createUser, check_user_pwd, get_mailbox, create_mailbox
from errors.nuerrors import NuMailError

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