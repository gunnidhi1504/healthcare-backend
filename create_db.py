"""
Script to create the PostgreSQL database for the healthcare project.
Handles connecting to the default 'postgres' database, checking if the target database exists,
and enabling autocommit mode so that CREATE DATABASE can execute outside a transaction block.
"""

import os
import sys
from pathlib import Path

# Load settings from .env file if available
try:
    from dotenv import load_dotenv
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / '.env')
except ImportError:
    pass

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("[!] Error: 'psycopg2' is not installed in your Python environment.")
    print("    Please run: pip install psycopg2-binary")
    sys.exit(1)


def create_healthcare_database():
    # Database connection parameters (connecting to maintenance DB 'postgres')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'missmago15')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    target_db = os.getenv('DB_NAME', 'healthcare_db')

    print("=" * 60)
    print("PostgreSQL Database Initialization")
    print("=" * 60)
    print(f"Target Database : {target_db}")
    print(f"Server Host     : {db_host}:{db_port}")
    print(f"User            : {db_user}")
    print("-" * 60)

    conn = None
    try:
        # Step 1: Connect to the default maintenance database 'postgres'
        print(f"[*] Connecting to maintenance database 'postgres'...")
        conn = psycopg2.connect(
            dbname='postgres',
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        # Step 2: Handle autocommit requirement
        # PostgreSQL cannot execute 'CREATE DATABASE' within a multi-statement transaction.
        # Setting autocommit = True ensures each statement is committed immediately.
        conn.autocommit = True
        print("[*] Autocommit enabled (required for CREATE DATABASE).")

        # Step 3: Check if database exists and create if needed
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s;",
                (target_db,)
            )
            exists = cursor.fetchone()

            if exists:
                print(f"[*] Database '{target_db}' already exists. No new database created.")
            else:
                # Use psycopg2.sql.Identifier to safely quote the database identifier
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db))
                )
                print(f"[✓] Database '{target_db}' created successfully!")

        print("[✓] Ready for Django migrations!")

    except psycopg2.OperationalError as e:
        print("\n[!] Connection Error: Could not connect to PostgreSQL server.")
        print(f"    Details: {e}")
        print("\n    Troubleshooting steps:")
        print("    1. Ensure your PostgreSQL service is running on your machine.")
        print("    2. Verify credentials in your .env file (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT).")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        sys.exit(1)
    finally:
        if conn is not None and not conn.closed:
            conn.close()
            print("[*] Database connection closed.")


if __name__ == '__main__':
    create_healthcare_database()
