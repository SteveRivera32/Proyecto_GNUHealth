from sqlalchemy import create_engine, text
import re
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

