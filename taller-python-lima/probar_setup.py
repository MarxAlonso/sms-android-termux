"""
Prueba de humo: corre esto UNA vez con tu API key para confirmar que TODO
funciona antes del taller (sin necesidad de abrir Streamlit).

    .venv/bin/python probar_setup.py

Lee la API key del entorno (GROQ_API_KEY) o de .streamlit/secrets.toml.
Si ves "✅ TODO OK", estás listo.
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")


def cargar_api_key() -> None:
    if os.environ.get("GROQ_API_KEY"):
        return
    try:
        import tomllib

        with open(".streamlit/secrets.toml", "rb") as f:
            os.environ["GROQ_API_KEY"] = tomllib.load(f)["GROQ_API_KEY"]
    except Exception:
        print(
            "❌ Falta GROQ_API_KEY.\n"
            "   Opción A: export GROQ_API_KEY=tu_key\n"
            "   Opción B: copia .streamlit/secrets.toml.example a "
            ".streamlit/secrets.toml y pega tu key.\n"
            "   Consíguela gratis en https://console.groq.com/keys"
        )
        sys.exit(1)


def main() -> None:
    cargar_api_key()

    # 1) ¿Existe la base de datos?
    if not os.path.exists("data/bodega.db"):
        print("❌ No existe data/bodega.db. Corre primero:  python data/generar_db.py")
        sys.exit(1)
    print("1/3  Base de datos encontrada ✅")

    # 2) ¿Importa el stack y construye el agente?
    from langchain.agents import create_agent
    from langchain_community.agent_toolkits import SQLDatabaseToolkit
    from langchain_community.utilities import SQLDatabase
    from langchain_groq import ChatGroq
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///file:data/bodega.db?mode=ro&uri=true")
    db = SQLDatabase(engine)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    agent = create_agent(
        llm,
        SQLDatabaseToolkit(db=db, llm=llm).get_tools(),
        system_prompt=(
            "Eres un agente que consulta una base de datos SQLite. Pasos en orden: "
            "lista las tablas, mira su esquema, escribe y verifica un SELECT, "
            "EJECÚTALO con sql_db_query y responde en español con el resultado. "
            "Solo SELECT, nunca modifiques datos."
        ),
    )
    print("2/3  Agente construido ✅")

    # 3) ¿Responde una pregunta real? (esto sí gasta 1 llamada al free tier)
    pregunta = "¿Cuántas ventas hay en total?"
    print(f"3/3  Preguntando al agente: «{pregunta}» ...")
    result = agent.invoke({"messages": [{"role": "user", "content": pregunta}]})
    print("     Respuesta:", result["messages"][-1].content.strip())

    print("\n✅ TODO OK — estás listo para el taller.")


if __name__ == "__main__":
    main()
