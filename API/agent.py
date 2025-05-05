from premsql.agents import BaseLineAgent
from premsql.generators import Text2SQLGeneratorOllama
from premsql.agents.tools import SimpleMatplotlibTool
from premsql.executors import SQLiteExecutor

import pandas as pd
import json
class Agent:
    def __init__(self):

        """Initialize the SQL agent with models and database connection."""
        self.model = Text2SQLGeneratorOllama(
            model_name="gemma3:4b",
            experiment_name="ollama",
            type="test",
            ollama_base_url="http://host.docker.internal:11434"
        )

        
        self.agent = BaseLineAgent(
            session_name="testing_ollama",
            db_connection_uri="sqlite:///california_schools.sqlite",
            specialized_model1=self.model,
            specialized_model2=self.model,
            plot_tool=SimpleMatplotlibTool(),
            executor=SQLiteExecutor()
        )
    
    def generate_response(self, question):
        """
        Generate a SQL response for the given natural language question.
        
        Args:
            question (str): The natural language question to convert to SQL
            
        Returns:
            tuple: (sql_string: SQL sentence, json_data: Query_Results )
        """
        

        response = self.agent(f"/query {question}")
        dataframe = response.show_output_dataframe()
        data_dict = dataframe.to_dict(orient='records')
        json_data = json.dumps(data_dict)
        print(json_data)





         
        return response.sql_string,json_data



