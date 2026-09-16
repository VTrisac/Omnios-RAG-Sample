# Preguntas de ejemplo

Estas preguntas están verificadas contra el corpus incluido en `data/`: el sistema, tal cual está,
devuelve el fragmento correcto en la primera posición. Sirven para comprobar que la instalación y el
pipeline funcionan antes de evaluar casos más difíciles.

```bash
python run.py "¿Cuál es el código de proveedor de Electromotores del Ebro?"
python run.py "¿Por qué se realizó la auditoría extraordinaria a Rodatec Levante?"
python run.py "¿Quién es la autora del informe técnico IT-2024-041?"
python run.py "¿Qué no conformidad mayor tiene Iberflex por el uso de un compuesto NBR no aprobado?"
```

| Pregunta | Documento esperado en el resultado #1 |
|---|---|
| ¿Cuál es el código de proveedor de Electromotores del Ebro? | `auditoria_proveedor_electromotores_ebro_2024.md` |
| ¿Por qué se realizó la auditoría extraordinaria a Rodatec Levante? | `auditoria_proveedor_rodatec_2024.md` |
| ¿Quién es la autora del informe técnico IT-2024-041? | `IT-2024-041_informe_tecnico.pdf` |
| ¿Qué no conformidad mayor tiene Iberflex por el uso de un compuesto NBR no aprobado? | `auditoria_proveedor_iberflex_2024.pdf` |
