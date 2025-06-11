# 🧠 GNU Health – Ejemplos de Consultas SQL

Este sistema trabaja con registros médicos. Las siguientes consultas SQL representan ejemplos de cómo interpretar solicitudes de usuarios en lenguaje natural. Usa estas estructuras como guía para construir nuevas consultas.

---

## 🔹 Ejemplo 1 – Casos de dengue por semana
**Pregunta del usuario:** Conteo de los casos de dengue por semana desde agosto del 2024 hasta enero del 2025.  
**SQL:**
```sql
SELECT 
  EXTRACT(YEAR FROM lab.create_date) AS año,
  EXTRACT(WEEK FROM lab.create_date) AS semana_epidemiologica,
  COUNT(*) AS total_casos
FROM public.gnuhealth_lab AS lab
WHERE 
  lab.serializer LIKE '%Positivo%' AND 
  lab.serializer LIKE '%Dengue%' AND 
  lab.date_analysis BETWEEN '2024-08-01' AND '2025-01-31'
GROUP BY año, semana_epidemiologica
ORDER BY año, semana_epidemiologica ASC;
```

---

## 🔹 Ejemplo 2 – Exámenes con resultados anormales
**Pregunta del usuario:** Lista de los exámenes de laboratorio ordenados por cantidad de resultados anormales.  
**SQL:**
```sql
SELECT
  DATE_TRUNC('month', lab.date_analysis) AS mes,
  test_type.name AS nombre_examen,
  COUNT(DISTINCT lab.patient) AS total_pacientes_anormales
FROM gnuhealth_lab AS lab
JOIN gnuhealth_lab_test_critearea AS criteria ON lab.id = criteria.gnuhealth_lab_id
JOIN gnuhealth_lab_test_type AS test_type ON lab.test = test_type.id
WHERE 
  lab.date_analysis BETWEEN '2024-08-01' AND '2025-01-31' AND (
    (criteria.result IS NOT NULL AND criteria.result >= criteria.lower_limit AND criteria.result <= criteria.upper_limit)
    OR
    (criteria.result IS NULL AND criteria.result_text ~ '^[0-9]+(\\.[0-9]+)?$' 
     AND criteria.result_text::DOUBLE PRECISION >= criteria.lower_limit 
     AND criteria.result_text::DOUBLE PRECISION <= criteria.upper_limit)
  )
GROUP BY mes, test_type.name
ORDER BY mes ASC, total_pacientes_anormales DESC;
```

---

## 🔹 Ejemplo 3 – Estado de control de pacientes con diabetes
**Pregunta del usuario:** Lista de pacientes con diabetes y su estado de control.  
**SQL:**
```sql
SELECT 
  d.name AS patient_id,
  CASE 
    WHEN lab.serializer IS NULL THEN 'Sin control' 
    ELSE lab.serializer 
  END AS casos_en_control
FROM gnuhealth_patient AS p
JOIN gnuhealth_patient_disease AS d ON p.name = d.name
JOIN gnuhealth_pathology AS pathology ON d.pathology = pathology.id
LEFT JOIN gnuhealth_lab AS lab ON p.name = lab.patient 
  AND LOWER(lab.serializer) LIKE '%glucosa%' 
  AND LOWER(lab.serializer) LIKE '%hp%'
WHERE LOWER(pathology.name) LIKE '%diabetes%'
ORDER BY d.name;
```

---

## 🔹 Ejemplo 4 – Casos de VIH por año, mes y género
**Pregunta del usuario:** Conteo de casos de VIH filtrados por mes, año y género.  
**SQL:**
```sql
SELECT 
  EXTRACT(YEAR FROM l.date_analysis) AS año,
  TO_CHAR(l.date_analysis, 'Month') AS mes,
  p.gender AS genero,
  COUNT(l.id) AS total_casos_vih
FROM gnuhealth_lab AS l
JOIN gnuhealth_patient AS gp ON l.patient = gp.id
JOIN party_party AS p ON gp.name = p.id
WHERE 
  l.serializer LIKE '%Positivo%' AND 
  l.serializer LIKE '%VIH%' AND 
  l.date_analysis BETWEEN '2024-08-01' AND '2025-01-31'
GROUP BY año, mes, p.gender
ORDER BY año DESC, mes, total_casos_vih DESC;
```

---

## 🔹 Ejemplo 5 – Pacientes con múltiples diagnósticos
**Pregunta del usuario:** Lista de pacientes con más de un diagnóstico y su cantidad.  
**SQL:**
```sql
SELECT 
  p.name AS patient_id,
  COUNT(d.pathology) AS numero_de_diagnosticos
FROM gnuhealth_patient AS p
JOIN gnuhealth_patient_disease AS d ON p.name = d.name
JOIN gnuhealth_pathology AS pathology ON d.pathology = pathology.id
GROUP BY p.name
HAVING COUNT(d.pathology) > 1
ORDER BY numero_de_diagnosticos DESC;
```

---

## 📌 Notas para el modelo:
- Usa `LIKE` para buscar términos médicos dentro de campos de texto (`serializer`, `pathology.name`, etc.).
- Fechas comunes: `'2024-08-01'` a `'2025-01-31'`.
- Agrupaciones y conteos son comunes para reportes epidemiológicos.
- Las relaciones clave entre pacientes, patologías y laboratorios se hacen mediante `JOIN`.

**Instrucción final:**  
Al generar una consulta SQL, selecciona las tablas y filtros más adecuados basándote en estos ejemplos, según lo que el usuario solicita en lenguaje natural.