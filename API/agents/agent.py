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
    
    def get_schema_summary(self, question: str):
        """
        Extrae el esquema de tablas relevantes en base a la pregunta e incluye descripción de columnas si está disponible.
        """
        try:
            from sqlalchemy import create_engine, text
            import re

            # Detectar nombres de tabla en la pregunta
            table_pattern = re.findall(r'\b(?:from|join|table)\s+([a-zA-Z_][\w]*)', question.lower())
            keywords = set(table_pattern)

            engine = create_engine("postgresql://admin:gnusolidario@localhost:5432/ghdemo44")
            tables = {}

            with engine.connect() as conn:
                # Obtener tablas relacionadas por claves foráneas
                fk_result = conn.execute(text("""
                    SELECT DISTINCT
                        tc.table_name AS source_table,
                        ccu.table_name AS target_table
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE 
                        constraint_type = 'FOREIGN KEY' AND
                        tc.table_schema = 'public';
                """))

                related_tables = set()
                for row in fk_result.fetchall():
                    source, target = row
                    if source in keywords or target in keywords:
                        related_tables.add(source)
                        related_tables.add(target)

                all_relevant_tables = keywords.union(related_tables)

                # Obtener columnas y descripciones
                if not all_relevant_tables:
                    return "No se pudo extraer el esquema relacionado con la pregunta."

                cols_result = conn.execute(text("""
                    SELECT 
                        cols.table_name, 
                        cols.column_name, 
                        pgd.description
                    FROM 
                        information_schema.columns cols
                    LEFT JOIN 
                        pg_catalog.pg_statio_all_tables st ON st.relname = cols.table_name
                    LEFT JOIN 
                        pg_catalog.pg_description pgd ON pgd.objoid = st.relid AND pgd.objsubid = cols.ordinal_position
                    WHERE 
                        cols.table_schema = 'public'
                    ORDER BY 
                        cols.table_name, cols.ordinal_position;
                """))

                for row in cols_result.fetchall():
                    table, column, description = row
                    if table in all_relevant_tables:
                        if table not in tables:
                            tables[table] = []
                        if description:
                            tables[table].append(f"{column} /* {description} */")
                        else:
                            tables[table].append(column)

            # Agregar descripciones específicas de tablas conocidas
            if "gnuhealth_ethnicity" in tables:
                tables["gnuhealth_ethnicity"] = [
                    "id",
                    "name /* nombre descriptivo de la etnia */",
                    "code /* código corto o clave técnica de la etnia */"
                ]

            if "gnuhealth_gender" in tables:
                tables["gnuhealth_gender"] = [
                    "id",
                    "name /* género descriptivo, como Masculino, Femenino, Otro */",
                    "code /* código usado internamente para representar el género */"
                ]

            if "gnuhealth_race" in tables:
                tables["gnuhealth_race"] = [
                    "id",
                    "name /* descripción de la raza del paciente */",
                    "code /* identificador técnico o abreviado de la raza */"
                ]

            if "gnuhealth_patient" in tables:
                tables["gnuhealth_patient"] = [
                    "id",
                    "name /* referencia a la persona en party_party */",
                    "ethnicity /* etnia del paciente */",
                    "race /* raza del paciente */",
                    "gender /* género del paciente */",
                    "dob /* fecha de nacimiento */",
                    "blood_type /* tipo sanguíneo del paciente */"
                ]

            if "party_party" in tables:
                tables["party_party"] = [
                    "id",
                    "name /* nombre completo de la persona o entidad */",
                    "du /* referencia al departamento o unidad regional */",
                    "active /* si la persona está activa en el sistema */"
                ]

            if "gnuhealth_du" in tables:
                tables["gnuhealth_du"] = [
                    "id",
                    "name /* nombre interno del departamento */",
                    "desc /* descripción del departamento o ubicación regional */"
                ]

            if "gnuhealth_person_alternative_identification" in tables:
                tables["gnuhealth_person_alternative_identification"] = [
                    "id",
                    "name /* referencia a la persona */",
                    "code /* código alternativo, como número de expediente u otra identificación */"
                ]

            if not tables:
                return "No se pudo extraer el esquema relacionado con la pregunta."

            schema_lines = [f"{t}({', '.join(cols)})" for t, cols in tables.items()]
            return "\n".join(schema_lines)

        except Exception as e:
            print("❌ Error extrayendo esquema:", e)
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
            schema_context = self.get_schema_summary(question)

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