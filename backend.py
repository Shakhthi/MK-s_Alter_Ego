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

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

with open("records.json", encoding="utf-8") as f:
    records = json.load(f)
record_user_details_json = records["record_user_details"]
record_unknown_question_json = records["record_unknown_question"]

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]

class MK:
    def __init__(self):
        groq_api_key = os.getenv('GROQ_API_KEY')
        self.groq = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
        self.name = "Mathanbabu Kaliappan"
        reader = PdfReader("data/LinkedIn_MK.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("data/summary_MK.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()
    
    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results

    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
        particularly questions related to {self.name}'s career, background, skills and experience. \
        Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
        You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
        Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
        If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
        If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt

    def chat(self, message, history):
        history = [{"role": h["role"], "content": h["content"]} for h in history]
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.groq.chat.completions.create(model="openai/gpt-oss-120b", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content

if __name__ == "__main__":
    me = MK()
    gr.ChatInterface(me.chat).launch()

