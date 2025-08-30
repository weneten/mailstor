"""Store e‑mail attachments in IMAP folders.

Attachments from all messages in the INBOX are uploaded back to the
mail server. For every 500 processed messages a new folder is created on
the server (``mailstor1``, ``mailstor2`` and so on) and the attachments
are saved there as individual messages. Credentials and server details
are loaded from a ``.env`` file.
"""
import os
import re
import imaplib
import email
import time
from email.message import EmailMessage
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
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=30)
    try:
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX")

        base_folder = "mailstor"
        folder_index = 1
        processed_count = 0
        current_folder = f"{base_folder}{folder_index}"
        mail.create(current_folder)

        status, data = mail.search(None, "ALL")
        if status != "OK":
            print("No messages found or unable to fetch IDs")
            return

        message_ids = data[0].split()

        for msg_id in message_ids:
            if processed_count >= 500:
                folder_index += 1
                processed_count = 0
                current_folder = f"{base_folder}{folder_index}"
                mail.create(current_folder)

            status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()
                if not filename:
                    continue
                safe_name = _sanitize_filename(filename)

                attachment_data = part.get_payload(decode=True)
                maintype = part.get_content_maintype()
                subtype = part.get_content_subtype()

                new_msg = EmailMessage()
                new_msg["Subject"] = safe_name
                new_msg.set_content("Attachment stored by mailstor")
                new_msg.add_attachment(
                    attachment_data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=safe_name,
                )

                mail.append(
                    current_folder,
                    "",
                    imaplib.Time2Internaldate(time.time()),
                    new_msg.as_bytes(),
                )

            processed_count += 1
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        try:
            mail.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()
