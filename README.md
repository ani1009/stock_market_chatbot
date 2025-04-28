# Indian-Stock-Market-Chatbot
This is a Indian Stock Market Chatbot Which Gives Information about NSE Stocks and it is LLM (Microsoft Phi) Powered Chatbot which Interacts With User and Give Response

File Contains two .py files: 1- chatbot.py and 2- chatbot1.py

To Run Both files you have to create virtual environment & after creating virtual environment you have to activate that environment by following command : .venv\Scripts\activate

After activating virtual environment you have to install Dependencies using pip command:pip install streamlit yfinance etc.

For First .py file run : streamlit run chatbot.py

For Second .py file run : streamlit run chatbot1.py

After Running chatbot.py File you will have Streamlit Interface and you will able to chat with chatbot: You can ask which is best performing stock, or any particular stock that you want

To run chatbot1.py file you must have to install some dependencies using pip command (in venv activated terminal): streamlit yfinance  plotly  numpy  langchain ollama

After Installing Dependencies You have to install Ollama in your Local System and you have to Download Phi-2: a 2.7B language model by Microsoft. here is the link: https://ollama.com/library/phi

After that you can run follwing command in your venv activated terminal: ollama list

You will see model named phi:latest (This is the AI Model which we Used)

After that You Just have to run command: ollama pull phi 

You will see ollama will Successfully able to pull phi model in youe venv

After performing all steps you just have to run chatbot1.py File using streamlit command & You Will AI Model's(Microsoft phi-2) Response You can ask bot questions like what is Stock, History of any Particular Stock etc.
