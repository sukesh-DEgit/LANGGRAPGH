import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langgraph.graph import START,END,StateGraph
import operator
from typing import TypedDict,Annotated
from langchain.messages import SystemMessage,AIMessage,HumanMessage,AnyMessage

import requests
import streamlit as st

from tools.flight_tool import search_flights
from tools.tavily_tool import tavily_search

llm = ChatGroq(model = "llama-3.3-70b-versatile")

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage],operator.add]
    user_query : str
    flight_results : str
    hotel_results :str
    Itinerary  : str
    llm_call : int


def flight_agent(state : TravelState):
    query = state["user_query"]
    flights_data = search_flights(query)
    return{
        "flight_results": flights_data,
        "messages": [AIMessage(content = f"Flight results fetched")],
        "llm_call":state.get("llm_call",0)+1
    }

def hotel_agent(state : TravelState):
    query =f"Best Hotels For {state["user_query"]}"
    hotel_data = tavily_search(query)
    return {
        "hotel_results" : hotel_data,
        "messages" : [AIMessage(content = f"hotel results Fetched")],
        "llm_call": state.get("llm_call",0)+1
    }

def Itinerary_agent(state : TravelState):
    prompt = f"""
        Create a Tarvel Itinerary
        User Query : {state['user_query']}
        Flight Results : {state['flight_results']}
        Hotel Results : {state['hotel_results']}
        """
    response = llm.invoke([
        SystemMessage(content = "You are a Travel Expert Planner"),
        HumanMessage (content = prompt)
    ])

    return {
        "Itinerary ": response.content,
        "message": [response],
        "llm_call": state.get('llm_call',0)+1
        }

def final_agent(state :TravelState):
    final_prompt = f""" Generate a Final Travel Response
    Flights : {state['flight_results']}
    Hotels : {state['hotel_results']}
    Itinerary  : {state['Itinerary']}
    """

    response = llm.invoke([HumanMessage(content = final_prompt)])
    # Another way to call LLM
    # response = llm.invoke(final_prompt)

graph = StateGraph(TravelState)

graph.add_node("Flight_agent",flight_agent)
graph.add_node("Hotel_agent",hotel_agent)
graph.add_node ("Itinerary_agent",Itinerary_agent)
graph.add_node("Final_agent",final_agent)


graph.add_edge(START,"Flight_agent")
graph.add_edge("Flight_agent","Hotel_agent")
graph.add_edge("Hotel_agent","Itinerary_agent")
graph.add_edge("Itinerary_agent","Final_agent")
graph.add_edge ("Final_agent",END)

app = graph.compile()
# app.get_graph().print_ascii()

if __name__ == "__main__":
    config = {
        "configurable":{
            "thread_id" :"user_name is sukesh"
        }
    }
# user_input = input("Enter Your Travel Plan: ")

st.title("Travel Agent")
user_input = st.text_input("Input Your Tarvel Plan")

if user_input:
    response = app.invoke(
        {
            "messages": [HumanMessage(content = user_input)],
            "user_query" : user_input,
            "flight_results": "",
            "Hotel_results": "",
            "Itinerary": "",
            "llm_call" : 0
        },config = config
        )
    st.write(response)