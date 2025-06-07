import json
from sqlalchemy import create_engine, text
import pandas as pd
import re
import os
#from generators.natural_ollama_model import TextGenerator
from generators.natural_ollama_model_v2 import TextGenerator
from premsql.executors import ExecutorUsingLangChain
from tabulate import tabulate
from typing import Optional

class Agent:
    def __init__(self, model_name: str):
        self.model = TextGenerator(model_name=model_name)
        self.executor = ExecutorUsingLangChain()
        self.db_uri = "postgresql://admin:gnusolidario@localhost:5432/ghdemo44"
        self.chat_history = []

    def load_prompt_template(self) -> str:
        base_path = os.path.dirname(__file__)
        prompt_path = os.path.join(base_path, "..", "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def load_context(self) -> str:
        base_path = os.path.dirname(__file__)
        prompt_path = os.path.join(base_path, "..", "context.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_schema_summary(self, question: str) -> str:
        try:
            table_pattern = re.findall(r'\b(?:from|join|table)\s+([a-zA-Z_][\w]*)', question.lower())
            keywords = set(table_pattern)

            engine = create_engine(self.db_uri)
            tables = {}

            with engine.connect() as conn:
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
                for source, target in fk_result.fetchall():
                    if source in keywords or target in keywords:
                        related_tables.update([source, target])

                all_relevant_tables = keywords.union(related_tables)

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

                for table, column, description in cols_result.fetchall():
                    if table in all_relevant_tables:
                        tables.setdefault(table, []).append(
                            f"{column} /* {description} */" if description else column
                        )

            # Campos extra manuales
            if "gnuhealth_ethnicity" in tables:
                tables["gnuhealth_ethnicity"] = ["id", "name /* nombre descriptivo de la etnia */", "code /* código corto o clave técnica de la etnia */"]

            if "gnuhealth_gender" in tables:
                tables["gnuhealth_gender"] = ["id", "name /* género descriptivo */", "code /* código técnico */"]


            if "gnuhealth_patient" in tables:
                tables["gnuhealth_patient"] = [
                    "id", "name /* persona */", "ethnicity", "race", "gender", "dob", "blood_type"
                ]

            if "party_party" in tables:
                tables["party_party"] = [
                    "id", "name /* nombre completo */", "du", "active"
                ]

            if "gnuhealth_du" in tables:
                tables["gnuhealth_du"] = [
                    "id", "name", "desc"
                ]

            if "gnuhealth_person_alternative_identification" in tables:
                tables["gnuhealth_person_alternative_identification"] = ["id", "name", "code"]

            schema_lines = [f"{t}({', '.join(cols)})" for t, cols in tables.items()]
            return "\n".join(schema_lines)

        except Exception as e:
            print("❌ Error extrayendo esquema:", e)
            return "No se pudo cargar el esquema."

    def remove_markdown(self, text: str) -> str:
        text2 = text.replace("json", " ")
        return text2.replace("```", " ")

    def query_model(self, messages: list, question: str, system_prompt: Optional[str] = None) -> dict:
        schema_context = self.get_schema_summary(question)
        extra_context = self.load_context()

        for attempt in range(4):
            print(f"🧠 Intento {attempt + 1}: Enviando prompt al modelo.")

            # Copiar el historial completo en cada intento
            attempt_messages = messages.copy()

            # Solo el primer intento debe incluir el system prompt original
            if attempt == 0 and system_prompt and not any(m["role"] == "system" for m in attempt_messages):
                attempt_messages.insert(0, {"role": "system", "content": system_prompt})

            # Si es un reintento y hubo JSON inválido, agregas aviso al user message
            if attempt == 0:
                user_content = f"{question}\n\nExtra Context:\n{extra_context}\n"
            else:
                user_content = (
                    "⚠️ Tu respuesta anterior no era JSON válido. "
                    "Asegúrate de responder solo con un objeto JSON correcto según las instrucciones.\n\n"
                    f"{question}\n\nExtra Context:\n{extra_context}\n"
                )

            # DEBUG → mostrar el array de mensajes que se envía
            print(f"📥 Enviando mensajes al modelo:")
            for m in attempt_messages:
                print(f"- {m['role']}: {m['content'][:100]}...")  # solo primeros 100 chars para no saturar
            print("\n")

            # Enviar al modelo
            raw = self.model.generate(attempt_messages)
            raw = self.remove_markdown(raw)
            print(f"📩 Respuesta RAW: {raw}")

            try:
                return json.loads(raw)
            except Exception as e:
                print(f"❌ Error al parsear JSON (intento {attempt + 1}):", str(e))

        return {"parse_error": "No se pudo obtener una respuesta JSON válida después de varios intentos."}

    def execute_sql(self, sql: str):
        try:
            engine = create_engine(self.db_uri)
            df = pd.read_sql(sql, engine)

            # Convertir columnas de tipo Timestamp a string
            for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']):
                df[col] = df[col].astype(str)

            # También pandas.Timestamp puede estar como object → convertir todo a string si es Timestamp
            for col in df.columns:
                df[col] = df[col].apply(lambda x: str(x) if isinstance(x, pd.Timestamp) else x)

            data = df.to_dict(orient="records")

            return {"result": data}
        except Exception as e:
            print("❌ Error al ejecutar SQL:", e)
            return {"error": str(e)}

    def json_to_markdown(self, json_data):
        # Si recibes un string JSON, lo conviertes a list/dict
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # Si es lista de dicts → tabla
        if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
            markdown_table = tabulate(json_data, headers="keys", tablefmt="github")
            return {"content": markdown_table}
        
        # Si es dict simple → lo formateas como bloque json
        elif isinstance(json_data, dict):
            return {"content": "```json\n" + json.dumps(json_data, indent=2, ensure_ascii=False) + "\n```"}
        
        else:
            raise ValueError("El formato JSON no es compatible (debe ser lista de dicts o dict simple).")

    def generate_response(self, question: str, system_prompt: Optional[str] = None) -> tuple:
        # Si es la primera llamada, inicializamos el chat_history con el system_prompt (si lo hay)
        if not hasattr(self, 'chat_history'):
            self.chat_history = []

        if not self.chat_history and system_prompt:
            self.chat_history.append({"role": "system", "content": system_prompt})

        # Construir el messages que se va a enviar esta vez
        messages = self.chat_history.copy()

        # Llamar a query_model con el historial completo
        response = self.query_model(messages, question, system_prompt)
        print("📥 Respuesta del modelo:", response)

        # Analizar la respuesta como antes
        if "parse_error" in response:
            return response, "error"

        if "content" in response:
            # Agregar la respuesta del modelo al historial
            self.chat_history.append({"role": "assistant", "content": response["content"]})
            return response, "natural"

        if "response" in response:
            self.chat_history.append({"role": "assistant", "content": response["response"]})
            return response, "natural"

        elif response.get("require") and "sql" in response:
            print("\n🟢 Entró al bloque SQL requerido")
            sql = response["sql"]
            print(f"▶ Ejecutando SQL: {sql}")

            for attempt in range(4):  # hasta 4 intentos
                execution_result = self.execute_sql(sql)
                print(f"🧪 Intento {attempt + 1}: Resultado de ejecución SQL:", execution_result)

                if "error" in execution_result:
                    print("🔁 Reintentando debido a error SQL...")
                    error_json = {"error": execution_result["error"]}
                    retry_messages = self.chat_history.copy()
                    retry_messages.append({"role": "user", "content": json.dumps(error_json)})
                    retry_response = self.model.generate(retry_messages)
                    try:
                        retry_json = json.loads(retry_response)
                        if retry_json.get("require") and "sql" in retry_json:
                            sql = retry_json["sql"]  # actualizar SQL con versión corregida
                        elif "content" in retry_json:
                            self.chat_history.append({"role": "assistant", "content": retry_json["content"]})
                            return retry_json, "natural"
                        else:
                            return {"parse_error": "Respuesta corregida no reconocida"}, "error"
                    except:
                        print("❌ El modelo devolvió un JSON inválido durante corrección de error.")
                        continue  # intentar de nuevo
                else:
                    print("\n✅ Entró al bloque para imprimir tabla")
                    print("📊 TABLA SQL EJECUTADA:")
                    print(tabulate(execution_result["result"], headers="keys", tablefmt="github"))

                    result_data = json.dumps(execution_result["result"], ensure_ascii=False)
                    result_prompt = f"{result_data}"
                    print("\n📤 Resultado SQL en JSON:\n", result_prompt)

                    # Aquí también puedes usar chat_history + nuevo user message si quieres
                    markdown_response = self.json_to_markdown(result_prompt)
                    print("\n📊 Tabla convertida a Markdown:\n", markdown_response)

                    self.chat_history.append({"role": "assistant", "content": markdown_response.get("content", "")})
                    
                    return markdown_response, "sql_result"

            return {"content": "No se pudo generar una respuesta válida después de varios intentos."}, "error"

        elif "error" in response:
            return response, "error"

        else:
            return {"parse_error": "Formato de respuesta no reconocido"}, "error"