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
from sqlalchemy import create_engine

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

        url = "postgresql://postgres:postgres@localhost:5432/db"
        self.agent = BaseLineAgent(
            session_name="testing_ollama",
            db_connection_uri="postgresql://admin:gnusolidario@localhost:5432/ghdemo44",
            specialized_model1=self.model,
            specialized_model2=None,
            plot_tool=SimpleMatplotlibTool(),
            executor=ExecutorUsingLangChain(),
        )
    
    def get_schema_summary(self, limit_tables=10):
        """
        Extrae el esquema de la base de datos PostgreSQL de tablas que comienzan con 'gnuhealth_'.
        Devuelve un resumen textual como: tabla(columna1, columna2)
        """
        try:
            from sqlalchemy import create_engine, text

            # Conexión directa a la base de datos
            engine = create_engine("postgresql://admin:gnusolidario@localhost:5432/ghdemo44")
            with engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT table_name, column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name LIKE 'gnuhealth_%'
                    ORDER BY table_name, ordinal_position
                """))

                tables = {}
                for row in result.fetchall():
                    table = row[0]
                    column = row[1]
                    if table not in tables:
                        tables[table] = []
                    tables[table].append(column)

            # Armar el texto final
            schema_lines = []
            for i, (table, columns) in enumerate(tables.items()):
                if i >= limit_tables:
                    break
                schema_lines.append(f"{table}({', '.join(columns)})")

            return "\n".join(schema_lines)

        except Exception as e:
            print("Error extrayendo esquema:", e)
            return "No se pudo cargar el esquema."

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

    
        return self.model.generate_stream({"prompt": question})
    

    def generate_natural_response(self, question: str) -> str:
        """
        Genera una respuesta en lenguaje natural para una pregunta dada.

        Args:
            question (str): Pregunta en lenguaje natural ingresada por el usuario.

        Returns:
            str: Respuesta generada por el modelo en lenguaje natural.
        """
        return self.model.generate({"prompt": question})
    
    def generate_sql_response(self, question: str):
        try:
            """
            Convierte una pregunta en lenguaje natural en una consulta SQL y la ejecuta sobre la base de datos.

            Args:
                question (str): Pregunta del usuario en lenguaje natural.

            Returns:
                str: Consulta SQL + tabla formateada, o mensaje de error.
            """

            # Obtener esquema y construir el prompt
            schema_context = self.get_schema_summary()

            prompt = (
                f"/query {question}\n"
                "Generate ONLY the PostgreSQL SQL query in a SINGLE LINE, "
                "do NOT include markdown formatting (no triple backticks, no indentation), "
                "do NOT include any text explanation or comments, "
                "ALWAYS end the query with a semicolon (;).\n\n"
                f"Tables:\n{schema_context}"
            )

            print("🧠 PROMPT ENVIADO AL MODELO:\n", prompt)

            # Enviar al modelo
            response = self.agent(prompt)

            print("🔍 Raw model response:\n", response)

            print("*" * 40)
            print("📝 Pregunta:", question)
            print("📄 SQL generado:", response.sql_string)
            print("*" * 40)

            # Verificar si el SQL fue generado correctamente
            if not response.sql_string or "SELECT" not in response.sql_string.upper():
                return "El modelo no generó una consulta SQL válida."

            # Obtener los datos
            data = response.sql_output_dataframe
            if not data or not isinstance(data, dict):
                return response.sql_string + "\n(No se obtuvieron resultados de la base de datos.)"

            cols = data.get("columns", [])
            values = data.get("data", {})

            if not cols or not values:
                return response.sql_string + "\n(Consulta ejecutada, pero sin resultados útiles.)"

            # Imprimir raw
            print("📦 Raw DataFrame:", data)

            # Formatear a tabla
            num_rows = max(len(v) for v in values.values())
            rows = []
            for i in range(num_rows):
                row = {col: values[col].get(i, "") for col in cols}
                rows.append(row)

            markdown_table = tabulate(rows, headers="keys", tablefmt="github")
            print("📊 Resultado formateado:\n", markdown_table)

            return response.sql_string + "\n" + markdown_table

        except Exception as e:
            print(f"❌ Error al generar o ejecutar SQL: {e}")
            return "No se pudo generar una consulta SQL válida para esta pregunta."

    def decide_response_type(self, question: str) -> str:
        decision_prompt = (
            f"Eres un experto que decide el mejor formato para responder preguntas: "
            f"consulta SQL o respuesta en lenguaje natural.\n\n"
            f"Instrucción: Dada la pregunta siguiente, responde solo con UNA palabra, "
            f"que debe ser 'SQL' si la respuesta requiere una consulta SQL, "
            f"o 'NATURAL' si debe responderse solo en lenguaje natural. "
            f"No escribas nada más, ni explicación.\n\n"
            f"Ejemplo:\n"
            f"Pregunta: ¿Cuántos empleados hay en la tabla?\n"
            f"Respuesta: SQL\n\n"
            f"Pregunta: ¿Qué es una base de datos?\n"
            f"Respuesta: NATURAL\n\n"
            f"Pregunta: {question}\n"
            f"Respuesta:"
        )
        decision = self.model.generate({"prompt": decision_prompt}).strip().upper()
        return decision

    def generate_response(self, question: str):
        decision = self.decide_response_type(question)
        # Imprimir la decisión
        print(f"Decision: {decision}")
        if decision == "SQL":
            response = self.generate_sql_response(question)
            return response, "sql"
        elif decision == "NATURAL":
            response = self.generate_natural_response(question)
            return response, "natural"
        else:
            return "No pude decidir cómo responder a tu pregunta.", "error"