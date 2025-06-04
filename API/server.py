from premsql.executors.from_langchain import ExecutorUsingLangChain
from premsql.playground import AgentServer
from premsql.generators.ollama_model import Text2SQLGeneratorOllama
from premsql.agents import BaseLineAgent
from premsql.agents.tools import SimpleMatplotlibTool
from generators.text2sql_google_model import Text2SQLGeneratorOpenAI
executor = ExecutorUsingLangChain()

from premsql.generators import Text2SQLGeneratorOllama
generator = Text2SQLGeneratorOllama(
    model_name="anindya/prem1b-sql-ollama-fp116",
    experiment_name="testing_ollama",
    type="test", 
)

analyser_plotter = Text2SQLGeneratorOpenAI(
    model_name="gemini-2.5-flash-preview-05-20",
    experiment_name="testing_ollama",
    type="test",
    openai_api_key="AIzaSyBcVCjbLebxXUDvO-QxPa7unFsaxg9nEyo"
)


agent = BaseLineAgent(
    session_name="TEST",
    db_connection_uri="postgresql://admin:gnusolidario@localhost:5432/ghdemo44",
    specialized_model1=generator,
    specialized_model2=analyser_plotter,
    executor=executor,
    plot_tool=SimpleMatplotlibTool()

)
agent_server = AgentServer(agent=agent, port=8263)
agent_server.launch()