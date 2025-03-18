import os
from postgres_da_ai_agent.modules.db import PostgresManager
from postgres_da_ai_agent.modules import llm
import dotenv
import argparse

dotenv.load_dotenv()

assert os.environ.get("DATABASE_URL"), "DATABASE_URL not found in .env file"

DB_URL = os.environ.get("DATABASE_URL")

POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
RESPONSE_FORMAT_CAP_REF = "RESPONSE_FORMAT"
SQL_DELIMITER = "---------"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="The prompt for the AI")
    args = parser.parse_args()

    if not args.prompt:
        print("Please provide a prompt")
        return

    prompt_str = f"Fulfill this database query: {args.prompt}. "

    with PostgresManager() as db:
        db.connect_with_url(DB_URL)
        table_definitions = db.get_table_definitions_for_prompt()

        # Attach table definitions to the prompt
        prompt_str = llm.add_cap_ref(
            prompt_str,
            f"Use these {POSTGRES_TABLE_DEFINITIONS_CAP_REF} to satisfy the database query.",
            POSTGRES_TABLE_DEFINITIONS_CAP_REF,
            table_definitions,
        )

        # Specify the expected response format so we can extract the SQL query easily.
        prompt_str = llm.add_cap_ref(
            prompt_str,
            f"\n\nRespond in this format {RESPONSE_FORMAT_CAP_REF}. Replace the text between <> with its request. I need to be able to easily parse the SQL query from your response.",
            RESPONSE_FORMAT_CAP_REF,
            f"""<explanation of the sql query>
{SQL_DELIMITER}
<sql query exclusively as raw text>""",
        )

        print("\n\n-------- PROMPT --------")
        print(prompt_str)

        # Generate response using the local Ollama model
        prompt_response = llm.prompt(prompt_str)
        print("\n\n-------- PROMPT RESPONSE --------")
        print(prompt_response)

        # Parse out the SQL query from the response
        sql_query = prompt_response.split(SQL_DELIMITER)[1].strip()
        print("\n\n-------- PARSED SQL QUERY --------")
        print(sql_query)

        result = db.run_sql(sql_query)
        print("\n\n======== POSTGRES DATA ANALYTICS AI AGENT RESPONSE ========")
        print(result)

if __name__ == "__main__":
    main()
