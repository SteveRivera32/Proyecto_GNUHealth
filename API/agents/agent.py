from premsql.agents import BaseLineAgent
from generators.text2sql_ollama_model import Text2SQLGeneratorOllama
from generators.text2sql_google_model import Text2SQLGeneratorOpenAI
from premsql.agents.tools import SimpleMatplotlibTool
from executors.postgre_executor import PostgreSQLExecutor
from generators.natural_ollama_model import TextGenerator 
from premsql.executors import ExecutorUsingLangChain
import pandas as pd
import os
from tabulate import tabulate
import json

class Agent:
    """
    Clase que representa un agente inteligente capaz de procesar preguntas en lenguaje natural
    y convertirlas en respuestas SQL o texto explicativo utilizando modelos de Ollama.

    Atributos:
        model (Text2SQLGeneratorOllama): Generador de instrucciones SQL desde texto.
        text_generator (TextGenerator): Generador de texto natural.
        agent (BaseLineAgent): Agente base que coordina la ejecución y herramientas.
    """
    
    def __init__(self, model_name: str):
        """
        Inicializa el agente con los modelos de generación de texto y SQL, así como la conexión a la base de datos.

        Args:
            model_name (str): Nombre del modelo Ollama a utilizar para generación de texto y SQL.
        """
        self.model = Text2SQLGeneratorOllama(
            model_name=model_name,
            experiment_name="ollama",
            type="test",
        )

       
        
        #self.text_generator = TextGenerator(model_name=model_name)
        #self.text_generator= Text2SQLGeneratorOpenAI(
        #     model_name=model_name,   # or your preferred model
        #     experiment_name="testing_openai",
        #     type="test",
        #     openai_api_key=os.getenv("OPENAI_API_KEY")  
        #     )
        

        url = "postgresql://postgres:postgres@localhost:5432/db"
        self.agent = BaseLineAgent(
            session_name="testing_ollama",
            db_connection_uri="postgresql://admin:gnusolidario@localhost:5432/ghdemo44",
            specialized_model1=self.model,
            specialized_model2=None,
            plot_tool=SimpleMatplotlibTool(),
            executor=ExecutorUsingLangChain(),
        )
    


    def generate_natural_response_stream(self, question: str) -> str:
        """
        Genera una respuesta en lenguaje natural para una pregunta dada.
        Y la envia en tiempo real al usuario. Esta opcion habilitada como meramente una prueba 
        para mostrar al usuario

        Args:
            question (str): Pregunta en lenguaje natural ingresada por el usuario.

        Returns:
            str: Respuesta generada por el modelo en lenguaje natural partida en Chunks 
        """

    
        return  self.text_generator.generate_stream(question)
    

    def generate_natural_response(self, question: str) -> str:
        """
        Genera una respuesta en lenguaje natural para una pregunta dada.

        Args:
            question (str): Pregunta en lenguaje natural ingresada por el usuario.

        Returns:
            str: Respuesta generada por el modelo en lenguaje natural.
        """
        return  self.text_generator.generate(question)
    
    def generate_sql_response(self, question: str):
        """
        Convierte una pregunta en lenguaje natural en una consulta SQL y la ejecuta sobre la base de datos.

        Args:
            question (str): Pregunta del usuario en lenguaje natural.

        Returns:
            Any: Resultado de la ejecución de la consulta SQL o error generado.
                  (Opcionalmente puede adaptarse para devolver dict o JSON)
        """
        response = self.agent(f"/query {question}"+". This is a Postgre SQL database.")
        print("*"*20)
        print(question)
        print(response.sql_string)
        print("*"*20)
        
        
        response = generator.generate_and_save_results(
           dataset=bird_dataset,
           temperature=0.1,
           max_new_tokens=256,
           force=True,
           executor=ExecutorUsingLangChain(),
           max_retries=5 # this is optional (default is already set to 5)
        )     
        
      
        data=response.sql_output_dataframe
        cols=data.get("columns")
        values=data.get("data")
        # Determinar número de filas
        
        print(data)
        num_rows = max(len(v) for v in values.values())
        
        # Construir lista de filas como diccionarios
        rows = []
        for i in range(num_rows):
            row = {col: values[col].get(i, "") for col in cols}
            rows.append(row)
        
        # Convertir a Markdown
        markdown_table = tabulate(rows, headers="keys", tablefmt="github")
        print(markdown_table)


        response = self.agent(f"/query {question}, always add the significant table to the output, exclude rows with null values, statscore table contans the schools statistics and schools table contain schoo information")
        
    
        return response.sql_string+"\n"+markdown_table
    
