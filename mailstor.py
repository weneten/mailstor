"""Simple IMAP attachment downloader.

Downloads attachments from all emails in the INBOX and stores them in
folder batches named ``mailstor1``, ``mailstor2`` and so on, with each
folder containing attachments from up to 500 emails. Credentials and
server details are loaded from a ``.env`` file.
"""
import os
import re
import imaplib
import email
from dotenv import load_dotenv

load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

if not all([IMAP_SERVER, EMAIL_USER, EMAIL_PASS]):
    raise ValueError("IMAP_SERVER, EMAIL_USER and EMAIL_PASS must be set in .env")


def _sanitize_filename(name: str) -> str:
    """Return a filename safe to use on most filesystems."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def main() -> None:
    # Connect to the IMAP server and fetch all message IDs
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("INBOX", readonly=True)

    status, data = mail.search(None, "ALL")
    if status != "OK":
        print("No messages found or unable to fetch IDs")
        mail.logout()
        return

    message_ids = data[0].split()

    base_folder = "mailstor"
    folder_index = 1
    processed_count = 0
    current_folder = f"{base_folder}{folder_index}"
    os.makedirs(current_folder, exist_ok=True)

    for msg_id in message_ids:
        if processed_count >= 500:
            folder_index += 1
            processed_count = 0
            current_folder = f"{base_folder}{folder_index}"
            os.makedirs(current_folder, exist_ok=True)

        status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        attachment_index = 0
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if not filename:
                continue
            attachment_index += 1
            safe_name = _sanitize_filename(filename)
            unique_name = f"{msg_id.decode()}_{attachment_index}_{safe_name}"
            filepath = os.path.join(current_folder, unique_name)
            with open(filepath, "wb") as f:
                f.write(part.get_payload(decode=True))

        processed_count += 1

    mail.logout()


if __name__ == "__main__":
    main()
