"""
Compile an email and deliver it via Amazon SES
"""

import os
import re
from pathlib import Path

from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3

from .logging import log

SES_SEND_IDENTITY = os.environ.get("SES_SEND_IDENTITY")


def strip_html(string):
    """Remove links and change HTML line breaks to plaintext."""

    # First, make concrete replacements
    string = (
        string.replace("<li>", "* ")
        .replace("<br/>", "\n")
        .replace("</li>", "\n")
        .replace("</p>", "\n")
    )

    # Don't allow double blank lines
    re.sub(r"\n{2,}", "\n\n", string)

    # Then look for links to replace
    re.sub(r'<a href="([^>]+)">.*</a>', r"\1", string)

    # Then finally, strip any other tags
    return re.sub(r"<[^>]+>", "", string)


def wrap_html(string):
    """Wrap the string in a default HTML document."""

    return (
        "<!doctype html>"
        "<html lang='en'>"
        "<head>"
        "<style>"
        ".error { color: red; }"
        "</style>"
        "</head>"
        f"<body>{string}</body>"
        "</html>"
    )


def send_email(**kwargs):
    """Send an email"""

    message = build_email(**kwargs)
    deliver_email(message)


def deliver_email(message: EmailMessage):
    """Deliver a constructed email via SES."""

    if not SES_SEND_IDENTITY:
        log.warning("No $SES_SEND_IDENTITY set. Skipping email delivery.")
        return

    client = boto3.client("ses")
    res = client.send_raw_email(
        Source=SES_SEND_IDENTITY,
        Destinations=message["to"].split(", "),
        RawMessage={
            "Data": message.as_string(),
        },
    )

    log.info("Send email result: %s", res)


def build_email(**kwargs) -> EmailMessage:
    """Construct an email message"""

    log.info("Building email")
    log.indent()

    message = EmailMessage()

    # Start with addressees. To is required, but the others are optional.
    message["To"] = kwargs["to"]
    log.info("To: %s", ", ".join(kwargs["to"]))

    if "cc" in kwargs:
        message["CC"] = kwargs["cc"]
        log.info("CC: %s", ", ".join(kwargs["bcc"]))
    if "bcc" in kwargs:
        message["BCC"] = kwargs["bcc"]
        log.info("BCC: %s", ", ".join(kwargs["bcc"]))

    # From is hard-coded. All message from the CI come from this address.
    name = kwargs.get("from_name", "MADS Course Builds")
    message["From"] = f"{name} <{SES_SEND_IDENTITY}>"
    log.info("From: %s", message["From"])

    # Subject is also required.
    message["Subject"] = kwargs["subject"]
    log.info("Subject: %s", kwargs["subject"])

    message.make_mixed()

    # Attach the main body of the message
    if "body" in kwargs:
        body = MIMEMultipart("alternative")
        body.attach(MIMEText(strip_html(kwargs["body"]), "plain", "utf-8"))
        body.attach(MIMEText(wrap_html(kwargs["body"]), "html", "utf-8"))
        message.attach(body)

        log.info("Body:")
        log.indent()
        log.info(strip_html(kwargs.get("body", "")))
        log.outdent()

    # Attach each of the attachments to the message
    if "attachments" in kwargs:
        log.info("Attachments:")
        log.indent("*")

        for att in kwargs.get("attachments", []):
            with open(att, "rb") as file:
                content = MIMEApplication(file.read())
                content.add_header(
                    "Content-Disposition", "attachment", filename=Path(att).name
                )
                message.attach(content)
                log.info(Path(att).name)

        log.outdent()

    log.info("")
    log.outdent()
    return message
