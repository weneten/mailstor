# MailStor

A simple utility that uses IMAP to download e-mail attachments and store
them in batches of 500 messages per folder. Folders are named
`mailstor1`, `mailstor2`, and so on.

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

The script will create folders `mailstor1`, `mailstor2`, etc., each
containing attachments for up to 500 emails from your inbox.
