# MailStor

A simple utility that uses IMAP to archive e‑mail attachments on the
server itself. Attachments from messages in the INBOX are uploaded as
separate messages to server-side folders named `mailstor1`, `mailstor2`
and so on, with each folder holding attachments from up to 500 e-mails.

## Setup

1. Create a `.env` file based on `.env.example` and provide your IMAP
   server and login credentials.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python mailstor.py
```

The script will create folders `mailstor1`, `mailstor2`, etc. **on the
IMAP server** and store attachments there as individual messages.

