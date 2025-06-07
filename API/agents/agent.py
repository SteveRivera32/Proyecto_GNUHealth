import json
from sqlalchemy import create_engine, text
import pandas as pd
import re
import os
from generators.natural_ollama_model import TextGenerator
from premsql.executors import ExecutorUsingLangChain
from module.tabulate_module import format_json_to_table
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
    
    def load_context(self) -> str:
        base_path = os.path.dirname(__file__)
        prompt_path = os.path.join(base_path, "..", "context.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    

    def execute_sql(self, sql: str):
        try:
            if "limit" not in sql.lower():
                sql = sql.strip().rstrip(';')
                sql = f"SELECT * FROM ({sql}) AS subquery LIMIT 100"
            
            engine = create_engine(self.db_uri)
            df = pd.read_sql(sql, engine)
            data = df.to_dict(orient="records")
            return {"result": data}
        except Exception as e:
            print("❌ Error al ejecutar SQL:", e)
            return {"error": str(e)}

    def json_to_markdown(json_data):
        pass
    
    def remove_markdown(self, text: str) -> str:
        text2 = text.replace("json", " ")
        return text2.replace("```", " ")

    def query_model(self, question: str) -> dict:
        prompt_template = self.load_prompt_template()


        for attempt in range(4):
            print(f"🧠 Intento {attempt + 1}: Enviando prompt al modelo.")
            

            #Condition removed to test the prompt
            prompt = f"{prompt_template}\nUser: {question}"
            #prompt = f"User: {question}"

            print(f"📥 Enviando prompt al modelo: {prompt}")
            raw = self.model.generate(prompt)
            raw = self.remove_markdown(raw)
            print(f"📩 Respuesta RAW:\n{raw}")
            try:
                return json.loads(raw)
            except Exception as e:
             
                print(f"❌ Error al parsear JSON (intento {attempt + 1}):", str(e))
                

        return {"parse_error": "No se pudo obtener una respuesta JSON válida después de varios intentos.","raw":raw}


    def generate_response(self, question: str):
        response = self.query_model(question)
        print("📥 Respuesta del modelo:", response)
    
        if "parse_error" in response:
            return response, "error"
    
        if "content" in response:
            return response, "natural"
    
        if "response" in response:
            return response, "natural"
    
        if response.get("require") and "sql" in response:
            print("🟢 Entró al bloque SQL requerido")
            sql = response["sql"]
            print(f"▶ Ejecutando SQL: {sql}")
            context = self.load_context()
    
            for attempt in range(4):
                execution_result = self.execute_sql(sql)
                print(f"🧪 Intento {attempt + 1}: Resultado de ejecución SQL:", execution_result)
    
                if "error" in execution_result:
                    print("🔁 Reintentando debido a error SQL...")
                    error = execution_result["error"]
                    retry_response = self.model.generate(
                        f'fix the SQL Code\ncontext:\n{context}\nthe error: {error}\n'
                        f'return the response as a JSON with no markdown, with format: {{"require": true, "sql": ""}}\n{question}'
                    )
    
                    try:
                        retry_json = json.loads(retry_response)
    
                        if retry_json.get("require") and "sql" in retry_json:
                            sql = retry_json["sql"]  # try again with new SQL
                        elif "content" in retry_json:
                            return retry_json, "natural"
                        else:
                            return {"parse_error": "Respuesta corregida no reconocida"}, "error"
    
                    except json.JSONDecodeError:
                        print("❌ El modelo devolvió un JSON inválido durante corrección de error.")
                        continue
    
                else:
                    print("✅ Entró al bloque para imprimir tabla")
                    try:
                        table = format_json_to_table(execution_result["result"])
                        print(table)
                        return {"table": table, "sql": sql}, "sql"
                    except Exception as e:
                        print("❌ Error formateando la tabla:", str(e))
                        return {"error": "Error al generar tabla Markdown."}, "error"
    
            return {"content": "No se pudo generar una respuesta válida después de varios intentos."}, "error"
    
        if "error" in response:
            return response, "error"
    
        return {"parse_error": "Formato de respuesta no reconocido"}, "error"
    