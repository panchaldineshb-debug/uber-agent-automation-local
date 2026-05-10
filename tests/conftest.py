import os

# Must be set before core.settings is imported by any test module
os.environ.setdefault("GMAIL_USER", "testadmin@gmail.com")
os.environ.setdefault("SON_EMAIL", "sameer@test.com")
