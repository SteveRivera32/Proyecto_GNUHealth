from premsql.agents import BaseLineAgent
from generators.text2sql_ollama_model import Text2SQLGeneratorOllama
from premsql.agents.tools import SimpleMatplotlibTool
from premsql.executors import SQLiteExecutor
from generators.natural_ollama_model import TextGenerator 
import pandas as pd
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
        
        self.text_generator = TextGenerator(model_name=model_name)
        
        self.agent = BaseLineAgent(
            session_name="testing_ollama",
            db_connection_uri="sqlite:///california_schools.sqlite",
            specialized_model1=self.model,
            specialized_model2=self.model,
            plot_tool=SimpleMatplotlibTool(),
            executor=SQLiteExecutor()
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
        response = self.agent(f"/query {question}")

        
        
        
      
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


        response = self.agent(f"/query {question}")
        
    
        return response.sql_string+"\n"+markdown_table
