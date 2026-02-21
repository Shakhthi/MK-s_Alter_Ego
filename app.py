import os
import json
from dotenv import load_dotenv

import requests
from pypdf import PdfReader

from openai import OpenAI
import gradio as gr

from schemas import PushoverPayload

load_dotenv(override=True)


def push(text) -> None:
    payload = PushoverPayload(
        token=os.getenv("PUSHOVER_TOKEN", ""),
        user=os.getenv("PUSHOVER_USER", ""),
        message=text,
    )
    requests.post(
        url="https://api.pushover.net/1/messages.json",
        data=payload.model_dump(),
    )

def push_user_details(name, email='not provided', notes='not provided'):
    push(f"Recording {name} with {email} with handed notes {notes}")
    return {'request':'ok'}