import os
import streamlit as st
from postgres_da_ai_agent.modules.db import PostgresManager
from postgres_da_ai_agent.modules import llm
import dotenv

dotenv.load_dotenv()

SQL_DELIMITER = "---------"

# Streamlit UI
st.title("PostgreSQL AI Query Generator")
st.write("Generate SQL queries using AI and execute them on your database.")

# User Input: Database URL
db_url = st.text_input("Enter your PostgreSQL Database URL", os.getenv("DATABASE_URL", ""))

# User Input: Query Prompt
user_prompt = st.text_area("Enter your natural language query:")

if st.button("Generate Query"):
    if not db_url:
        st.error("Please provide a valid database URL.")
    elif not user_prompt:
        st.error("Please enter a query prompt.")
    else:
        with PostgresManager() as db:
            db.connect_with_url(db_url)
            table_definitions = db.get_table_definitions_for_prompt()

            prompt_str = f"Fulfill this database query: {user_prompt}. "
            prompt_str = llm.add_cap_ref(
                prompt_str,
                "Use these TABLE_DEFINITIONS to satisfy the database query.",
                "TABLE_DEFINITIONS",
                table_definitions,
            )

            prompt_str = llm.add_cap_ref(
                prompt_str,
                f"\n\nRespond in this format RESPONSE_FORMAT. Replace the text between <> with its request. I need to be able to easily parse the SQL query from your response.",
                "RESPONSE_FORMAT",
                f"""<explanation of the sql query>
{SQL_DELIMITER}
<sql query exclusively as raw text>""",
            )

            # Generate response from AI
            prompt_response = llm.prompt(prompt_str)
            sql_query = prompt_response.split(SQL_DELIMITER)[1].strip()

            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            # Execute SQL Query
            result = db.run_sql(sql_query)
            st.subheader("Query Result")
            st.write(result)
