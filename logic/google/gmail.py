import os
import base64
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Literal

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import config

class Gmail:
    def __init__(self, credentials_file='logic/google/credentials.json', token_file='logic/google/token.pickle'):
        """
        Initialize the Gmail API client.

        Args:
            credentials_file (str): Path to the OAuth2 credentials JSON file from Google Cloud.
            token_file (str): Path to the file where the authentication token will be cached.
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._get_service()

    def _get_service(self):
        creds = Credentials(
            token=None,
            refresh_token=config.GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config.GOOGLE_CLIENT_ID,
            client_secret=config.GOOGLE_CLIENT_SECRET,
        )

        return build("gmail", "v1", credentials=creds)
    

    def send(
        self,
        body=None,
        sender=None,
        recipient='rejoicechinwendu01@gmail.com',
        subject=None,
        cc=None,
        bcc=None,
        attachments=None,
        format: Literal['html', 'plain'] = 'plain'
    ):
        # Use alternative for HTML so clients can render properly
        if format == 'html':
            message = MIMEMultipart('alternative')
        else:
            message = MIMEMultipart()

        message['From'] = sender
        message['To'] = recipient

        if subject:
            message['Subject'] = subject

        if cc:
            message['Cc'] = cc

        if bcc:
            message['Bcc'] = bcc

        # Attach email body
        if body:
            message.attach(
                MIMEText(
                    body,
                    format,
                    'utf-8'
                )
            )

        # Attach files
        if attachments:
            for file_path in attachments:

                if not os.path.isfile(file_path):
                    continue

                content_type, encoding = mimetypes.guess_type(file_path)

                if content_type is None or encoding is not None:
                    content_type = 'application/octet-stream'

                main_type, sub_type = content_type.split('/', 1)

                with open(file_path, 'rb') as f:
                    mime_base = MIMEBase(main_type, sub_type)
                    mime_base.set_payload(f.read())

                encoders.encode_base64(mime_base)

                mime_base.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(file_path)
                )

                message.attach(mime_base)

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        try:
            response = (
                self.service
                .users()
                .messages()
                .send(
                    userId='me',
                    body={'raw': raw_message}
                )
                .execute()
            )

            return response

        except Exception as e:
            print(f'Failed to send email: {e}')
            raise




    def send1(self,body=None, sender = None, recipient  = 'rejoicechinwendu01@gmail.com', subject=None, cc=None, bcc=None, attachments=None, format: Literal['html', 'plain'] = 'plain'):
        """
        Send an email with optional attachments.

        Args:
            sender (str): Sender email address.
            recipient (str): Recipient email address.
            subject (str): Email subject line.
            body (str): Email body text.
            cc (str, optional): CC email addresses.
            bcc (str, optional): BCC email addresses.
            attachments (list, optional): List of file paths to attach.

        Returns:
            dict: API response from Gmail.
        """
        # Create a multipart container
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient
        if subject:
            message['Subject'] = subject
        if cc:
            message['Cc'] = cc
        if bcc:
            message['Bcc'] = bcc

        # Attach the email body
        if body:
            message.attach(MIMEText(body, format))

        # Attach files if provided
        if attachments:
            for file_path in attachments:
                if not os.path.isfile(file_path):
                    continue  # skip if file doesn't exist

                content_type, encoding = mimetypes.guess_type(file_path)
                if content_type is None or encoding is not None:
                    content_type = 'application/octet-stream'

                main_type, sub_type = content_type.split('/', 1)
                with open(file_path, 'rb') as f:
                    mime_base = MIMEBase(main_type, sub_type)
                    mime_base.set_payload(f.read())

                encoders.encode_base64(mime_base)
                mime_base.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                message.attach(mime_base)

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send via Gmail API
        try:
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
                ).execute()
            return 1
        except:
            return 


    def read(self, email, n=None, as_thread = False):
        """
        Read conversation history involving an email address.

        Args:
            email (str): Email address to search for.
            n (int, optional): Maximum number of threads to return.

        Returns:
            list: List of conversation threads.
        """

        query = f"from:{email} OR to:{email}"

        results = self.service.users().threads().list(
            userId="me",
            q=query
        ).execute()

        threads = results.get("threads", [])

        if n:
            threads = threads[:n]

        conversations = []

        for thread in threads:
            thread_data = self.service.users().threads().get(
                userId="me",
                id=thread["id"],
                format="full"
            ).execute()

            messages = []

            for msg in thread_data.get("messages", []):

                headers = {
                    h["name"]: h["value"]
                    for h in msg["payload"].get("headers", [])
                }

                body = ""

                if "parts" in msg["payload"]:
                    for part in msg["payload"]["parts"]:
                        if part.get("mimeType") == "text/plain":
                            data = part["body"].get("data")
                            if data:
                                body = base64.urlsafe_b64decode(
                                    data.encode()
                                ).decode(errors="ignore")
                                break

                else:
                    data = msg["payload"]["body"].get("data")
                    if data:
                        body = base64.urlsafe_b64decode(
                            data.encode()
                        ).decode(errors="ignore")

                messages.append({
                    "message_id": msg["id"],
                    "from": headers.get("From"),
                    "to": headers.get("To"),
                    "subject": headers.get("Subject"),
                    "date": headers.get("Date"),
                    "body": body.strip()
                })

            conversations.append({
                "thread_id": thread["id"],
                "messages": messages
            })

        return conversations

if __name__ == '__main__':
	gmail = Gmail()
	gmail.send(
	sender = 'freonkarl@gmail.com',
	recipient = 'rejoicechinwendu01@gmail.com',
	subject = 'trial',
	body = 'tries'
	)