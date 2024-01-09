#! -*- coding:utf-8 -*-
import openai
import configparser
import logging
from colorama import Fore, Style
import os
from pathlib import Path
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

# Load config
config = configparser.ConfigParser()
config.read(os.path.join(Path(__file__).parent, "./openai_config.ini"))

# Setting logging & logging format
LOGGING_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATE_FORMAT = r"%Y%m%d %H:%M:%S"
logging.basicConfig(level = logging.INFO, format = LOGGING_FORMAT, datefmt = DATE_FORMAT)

# OpenAI API setting
api_key = str(config['openai_api']['private_key'])
openai.api_key = api_key

def loadPromptTemplate(file_path: str, file_name: str) -> str:
    f = open(f"{file_path}{file_name}.txt", "r")
    prompt_template = f.read()
    f.close()
    return prompt_template

def writePromptFile(file_path: str, file_name: str, content: str):
    text_file = open(f"{file_path}{file_name}.txt", "w")
    text_file.write(content)
    text_file.close()

class Chatbot():
    def __init__(self, role, conversation_summary):
        self.llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-4", temperature=0)
        self.role = role
        self.role_prompt = loadPromptTemplate(os.path.join(Path(__file__).parent, "./prompt/"), self.role)
        if len(conversation_summary) != 0:
            self.role_prompt = self.role_prompt + conversation_summary
        self.chat_history = ""
        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    self.role_prompt
                ),
                # The `variable_name` here is what must align with memory
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}"),
            ]
        )
        # Notice that we `return_messages=True` to fit into the MessagesPlaceholder
        # Notice that `"chat_history"` aligns with the MessagesPlaceholder name
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.conversation = LLMChain(llm=self.llm, prompt=self.prompt, verbose=False, memory=self.memory)
    def chat(self, question:str) -> str:
        # Notice that we just pass in the `question` variables - `chat_history` gets populated by memory
        result = self.conversation({"question": question})
        answer = result['text']
        if self.role == "role_customer":
            self.chat_history = self.chat_history + f"理專: '{question}', 客戶: '{result['text']}'\n"
        elif self.role == "role_mentor":
            self.chat_history = self.chat_history + f"教練: '{question}', 理專: '{result['text']}'\n"
        return answer


class CtbcAIMentor():
    def __init__(self):
        self.max_chat_cnt = 10
        self.chat_cnt = 1
    def mainChat(self):
        customer = Chatbot("role_customer", "")
        while True:
            question = input("Q: ")
            if question == "exits" or self.chat_cnt >= self.max_chat_cnt:
                break
            elif question == "mentor":
                mentor = Chatbot("role_mentor", customer.chat_history)
                answer = mentor.chat("請評價我作為理專與顧客對話的表現")
                print(answer)
                break
            else:
                answer = customer.chat(question)
                print(answer)
            self.chat_cnt += 1

if __name__ == "__main__":
    ctbcAiMentor = CtbcAIMentor()
    ctbcAiMentor.mainChat()
    