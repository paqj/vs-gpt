from langchain.tools import DuckDuckGoSearchResults
import yfinance
import json
import streamlit as st
import openai as client
import time
import os


st.set_page_config(
    page_title="AssistantGPT",
    page_icon="💼",
)

st.markdown(
    """
    # AssistantGPT
            
    Welcome to AssistantGPT.
            
    Write down the name of a company and our Agent will do the research for you.
"""
)

company = st.text_input("Write the name of the company you are interested on.")

# 임시
assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")

# Tools
def get_ticker(inputs):
    ddg = DuckDuckGoSearchResults()
    company_name = inputs["company_name"]
    return ddg.run(f"Ticker symbol of {company_name}")

def get_income_statement(inputs):
    ticker = inputs["ticker"]
    stock = yfinance.Ticker(ticker)
    return json.dumps(stock.income_stmt.to_json())

def get_balance_sheet(inputs):
    ticker = inputs["ticker"]
    stock = yfinance.Ticker(ticker)
    return json.dumps(stock.balance_sheet.to_json())


def get_daily_stock_performance(inputs):
    ticker = inputs["ticker"]
    stock = yfinance.Ticker(ticker)
    return json.dumps(stock.history(period="3mo").to_json())

functions_map = {
    "get_ticker": get_ticker,
    "get_income_statement": get_income_statement,
    "get_balance_sheet": get_balance_sheet,
    "get_daily_stock_performance": get_daily_stock_performance,
}

functions = [
    {
        "type": "function",
        "function": {
            "name": "get_ticker",
            "description": "Given the name of a company returns its ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "The name of the company",
                    }
                },
                "required": ["company_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_income_statement",
            "description": "Given a ticker symbol (i.e AAPL) returns the company's income statement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Ticker symbol of the company",
                    },
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_balance_sheet",
            "description": "Given a ticker symbol (i.e AAPL) returns the company's balance sheet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Ticker symbol of the company",
                    },
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_stock_performance",
            "description": "Given a ticker symbol (i.e AAPL) returns the performance of the stock for the last 100 days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Ticker symbol of the company",
                    },
                },
                "required": ["ticker"],
            },
        },
    },
]

def setup_openai_assistant():
    if 'assistant' not in st.session_state:
        st.session_state.assistant = client.beta.assistants.create(
            name="Investor Assistant For Streamlit",
            instructions="You help users do research on publicly traded companies and you help users decide if they should buy the stock or not.",
            model="gpt-4-1106-preview", # https://platform.openai.com/playground?mode=assistant : Model List
            tools=functions,
        )

    return st.session_state.assistant

def get_run(run_id, thread_id):
    return client.beta.threads.runs.retrieve(
        run_id=run_id,
        thread_id=thread_id,
    )

def send_message(thread_id, content):
    return client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=content
    )

def get_messages(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    messages = list(messages)
    messages.reverse()
    for message in messages:
        content = message.content[0].text.value.replace("$", "\$")

        st.write(f"{message.role}: {content}")

def get_tool_outputs(run_id, thread_id):
    run = get_run(run_id, thread_id)
    outputs = []

    for action in run.required_action.submit_tool_outputs.tool_calls:
        action_id = action.id
        function = action.function
        
        st.write(f"Calling function: {function.name} with arg {function.arguments}")
        
        outputs.append(
            {
                "output": functions_map[function.name](json.loads(function.arguments)),
                "tool_call_id": action_id,
            }
        )
    return outputs

def submit_tool_outputs(run_id, thread_id):
    outputs = get_tool_outputs(run_id, thread_id)
    return client.beta.threads.runs.submit_tool_outputs(
        run_id=run_id, thread_id=thread_id, tool_outputs=outputs
    )

if company:
    # assistant_id = assistant_id
    assistant = setup_openai_assistant()

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": f"I want to know if the {company} stock is a good buy",
            }
        ]
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        # assistant_id=assistant_id,
        assistant_id=assistant.id,
    )

    status = get_run(run.id, thread.id).status

    while status != "completed":
        if status == "requires_action":
            submit_tool_outputs(run.id, thread.id)

        time.sleep(2)

        status = get_run(run.id, thread.id).status

    get_messages(thread.id)