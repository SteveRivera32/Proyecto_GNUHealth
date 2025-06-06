import json
from sqlalchemy import create_engine, text
import pandas as pd
import re
import os
from generators.natural_ollama_model import TextGenerator
from premsql.executors import ExecutorUsingLangChain
from tabulate import tabulate

class Agent:
    def __init__(self, model_name: str):
        self.model = TextGenerator(model_name=model_name)
        self.executor = ExecutorUsingLangChain()
        self.db_uri = "postgresql://admin:gnusolidario@localhost:5432/ghdemo44"

    def load_prompt_template(self) -> str:
        base_path = os.path.dirname(__file__)
        prompt_path = os.path.join(base_path, "..", "prompt.txt")
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

    def query_model(self, question: str) -> dict:
        schema_context = self.get_schema_summary(question)
        prompt_template = self.load_prompt_template()

        for attempt in range(4):
            print(f"🧠 Intento {attempt + 1}: Enviando prompt al modelo.")
            if attempt == 0:
                prompt = f"{prompt_template}\n\nUser: {question}\nTables:\n{schema_context}"
            else:
                prompt = (
                    f"{prompt_template}\n\n"
                    f"⚠️ Tu respuesta anterior no era JSON válido. "
                    f"Asegúrate de responder solo con un objeto JSON correcto según las instrucciones.\n\n"
                    f"User: {question}\nTables:\n{schema_context}"
                )

            raw = self.model.generate(prompt)
            print(f"📩 Respuesta RAW:\n{raw}")
            try:
                return json.loads(raw)
            except Exception as e:
                print(f"❌ Error al parsear JSON (intento {attempt + 1}):", str(e))

        return {"parse_error": "No se pudo obtener una respuesta JSON válida después de varios intentos."}


    def execute_sql(self, sql: str):
        try:
            engine = create_engine(self.db_uri)
            df = pd.read_sql(sql, engine)
            data = df.to_dict(orient="records")
            return {"result": data}
        except Exception as e:
            print("❌ Error al ejecutar SQL:", e)
            return {"error": str(e)}

    def generate_response(self, question: str):
        response = self.query_model(question)
        print("📥 Respuesta del modelo:", response)

        if "parse_error" in response:
            return response, "error"

        if "content" in response:
            return response, "natural"

        elif response.get("require") and "sql" in response:
            print("🟢 Entró al bloque SQL requerido")
            sql = response["sql"]
            print(f"▶ Ejecutando SQL: {sql}")

            for attempt in range(4):  # hasta 4 intentos
                execution_result = self.execute_sql(sql)
                print(f"🧪 Intento {attempt + 1}: Resultado de ejecución SQL:", execution_result)

                if "error" in execution_result:
                    print("🔁 Reintentando debido a error SQL...")
                    error_json = {"error": execution_result["error"]}
                    retry_prompt = json.dumps(error_json)
                    retry_response = self.model.generate(retry_prompt)
                    try:
                        retry_json = json.loads(retry_response)
                        if retry_json.get("require") and "sql" in retry_json:
                            sql = retry_json["sql"]  # actualizar SQL con versión corregida
                        elif "content" in retry_json:
                            return retry_json, "natural"
                        else:
                            return {"parse_error": "Respuesta corregida no reconocida"}, "error"
                    except:
                        print("❌ El modelo devolvió un JSON inválido durante corrección de error.")
                        continue  # intentar de nuevo
                else:
                    print("✅ Entró al bloque para imprimir tabla")
                    print("\n📊 TABLA SQL EJECUTADA:")
                    print(tabulate(execution_result["result"], headers="keys", tablefmt="github"))

                    result_data = json.dumps(execution_result["result"], ensure_ascii=False)
                    result_prompt = f"{result_data}"
                    markdown_response = self.model.generate(result_prompt)
                    try:
                        markdown_json = json.loads(markdown_response)
                        return markdown_json, "sql_result"
                    except:
                        return {"parse_error": "Error formateando resultado SQL"}, "error"

            return {"content": "No se pudo generar una respuesta válida después de varios intentos."}, "error"

        elif "error" in response:
            return response, "error"

        else:
            return {"parse_error": "Formato de respuesta no reconocido"}, "error"