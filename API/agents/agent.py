import json
from sqlalchemy import  text
import pandas as pd
from sqlalchemy.orm import Session
import re
import os
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, IntegrityError, OperationalError
import redis_db.redis_kb_module as kb
from generators.natural_ollama_model import TextGenerator
from tabulate import tabulate
from typing import Optional
from langchain.utilities import SQLDatabase
import pandas as pd

class Agent:
    def __init__(self, model_name: str):
        self.model = TextGenerator(model_name=model_name)
        self.db_uri = "postgresql+pg8000://admin:gnusolidario@localhost:5432/ghdemo44"
        self.chat_history = []
        self.system_prompt=""

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

    def remove_markdown(self,text: str) -> str:
        # Remove code block markdown with optional language label (like ```json)
        clean_text = re.sub(r"```(?:\w+)?\n?", "", text)
        # Remove trailing triple backticks if still present
        clean_text = re.sub(r"\n?```", "", clean_text)
        return clean_text.strip()

    def query_model(self, messages: list, question: str) -> dict:

       
        messages.append( {"role": "user", "content": question})

        for attempt in range(4):

            """Este ciclo for fuerza al modelo a generar un json  no tiene nada que ver con SQL
                Seria recomendable cambiar le nombre de esta funcion 
            """
            # Enviar al modelo
            raw = self.model.generate(messages)
            raw = self.remove_markdown(raw)
            messages.append({"role": "assistant", "content": raw})
        

            try:
                return json.loads(raw)
            except Exception as e:
                user_content = (
                    "Tu respuesta anterior no era JSON válido. "
                    "Asegúrate de responder solo con un objeto JSON correcto según las instrucciones.\n\n"
                    f"\n {raw}")
                messages.append( {"role": "user", "content": user_content})
                print(f"❌ Error al parsear JSON (intento {attempt + 1}):", str(e))

        return {"parse_error": "No se pudo obtener una respuesta JSON válida después de varios intentos."}

    def execute_sql(self, sql: str):
        try:
            sql_lower = sql.lower()
            forbidden_statements = {
                "delete": "❌ No está permitido ejecutar sentencias DELETE.",
                "update": "❌ No está permitido ejecutar sentencias UPDATE.",
                "insert": "❌ No está permitido ejecutar sentencias INSERT.",
                "drop": "❌ No está permitido ejecutar sentencias DROP.",
                "alter": "❌ No está permitido ejecutar sentencias ALTER.",
                "truncate": "❌ No está permitido ejecutar sentencias TRUNCATE.",
                "create": "❌ No está permitido ejecutar sentencias CREATE.",
            }

            for statement, message in forbidden_statements.items():
                if re.search(rf"\b{statement}\b", sql_lower):
                    return {"error": message}

            db = SQLDatabase.from_uri(self.db_uri)

            with db._engine.connect() as conn:
                df = pd.read_sql(sql, conn)

            # Convertir timestamps a string
            for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']):
                df[col] = df[col].astype(str)

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


    def get_route(self,response: dict):
        

        if "content" in response:
            # Agregar la respuesta del modelo al historial
            self.chat_history.append({"role": "assistant", "content": response["content"]})
            return "CONTENT"

        elif "response" in response:
            self.chat_history.append({"role": "assistant", "content": response["response"]})
            return "RESPONSE"
        elif "sql" in response:
            #convertimos el diccionario en string se lo madnamos de regreso al LLM
            self.chat_history.append({"role":"assistant","content":json.dumps(response)})
            return "SQL"
        
        return "CONTENT"

    def get_sql_error(self,sql_alchemy_execpetion):
        
        match = re.search(r"'M': '(.*?)'(?:,|$|})", sql_alchemy_execpetion)

        if match:
            # Group 1 (the first capturing group) contains the actual message
            db_error_message = match.group(1)
        else:
            # If the regex doesn't find the 'M' pattern, use the full string as a fallback
            db_error_message = sql_alchemy_execpetion
        return db_error_message

    # we need to implement a self correctipon algorithm
    def retry_sql(self, sql_error,sql="", users_question="",chat_history=None,attempts=4):
        # for thius we will need to start a new chat with the LLM
        if chat_history==None:
            
            chat_history=[]
            chat_history.append({"role":"system","content":self.system_prompt})
        result={"error":0}
        for attempt in range(attempts):

            if "error" in result:
                    

                print(f"Intento {attempt}:\n ")
    
                prompt=f'UserQuestion:{users_question} ExecutedSQL:{sql} \nSQLError:{sql_error} \n'
                if(attempt==0):
                    prompt+="\n Database Schema:\n"+kb.build_few_shot_prompt(prompt)
    
                response=self.query_model(chat_history,prompt)
                #chat_history.append({"role":"assistant","content":json.dumps(response)})

    
                route=self.get_route(response)
                if route=="SQL":
                    result=self.execute_sql(sql)
            else:
                return result 
        
        return "error"



                
    
        
        
        
    

    def generate_response(self, question: str, system_prompt: Optional[str] = None) -> tuple:
        # Si es la primera llamada, inicializamos el chat_history con el system_prompt (si lo hay)
        self.system_prompt=system_prompt
        if not hasattr(self, 'chat_history'):

            self.chat_history = []

        if not self.chat_history and system_prompt:
            self.chat_history.append({"role": "system", "content": system_prompt})
            
            # Guaradamos el system prompt

        # Construir el messages que se va a enviar esta vez
        messages = self.chat_history.copy()
        extra_context = kb.build_few_shot_prompt(question) + "\n"+f"UserQuestion:{question}"
        response = self.query_model(messages, extra_context)
        next_route=self.get_route(response)
       
        if next_route=="SQL":
           
            sql=response["sql"]
            execution_result = self.execute_sql(sql)


            print(f"▶ Ejecutando SQL: {sql}")
            print(execution_result)    
                
            if "error" in execution_result:
                if any(keyword in execution_result["error"].lower() for keyword in ["no está permitido", "no se permite"]):
                        #Filtra preguntas no desaedas
                    return {"content": execution_result["error"]}, "natural"
                    
                # si no obtenemos el error de SQL Alchemy
                db_error_message=self.get_sql_error(execution_result["error"])  
                print(f"\n ERROR Intento : Resultado de ejecución SQL:", db_error_message+"\n")
                print(f"🔁 Reintentando: debido a error SQL...")
                #Creamos un nuevo chat con el modelo para intentar resolver el problema
                result=self.retry_sql(sql_error=db_error_message,sql=sql,users_question=question)

                if result=="error":
                    return {"content": "No se pudo generar una respuesta válida después de varios intentos."}, "error"
                else:
                    execution_result=result

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
        elif next_route == "RESPONSE":
            return response, "natural"


        elif next_route == "CONTENT":
            return response, "natural"

        elif "error" in response:
            return response, "error"

        else:
            return {"parse_error": "Formato de respuesta no reconocido"}, "error"

        