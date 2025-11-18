#!/usr/bin/env python3
"""
Database migration helper script.

This script provides a convenient interface to Alembic migrations
for the PPE detection database.

Usage:
    python migrate.py upgrade        # Upgrade to latest
    python migrate.py downgrade      # Downgrade one version
    python migrate.py current        # Show current version
    python migrate.py history        # Show migration history
    python migrate.py create "msg"   # Create new migration
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def run_alembic_command(args):
    """Run alembic command with proper configuration."""
    from alembic.config import Config
    from alembic import command

    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    alembic_ini = script_dir / "alembic.ini"

    if not alembic_ini.exists():
        print(f"Error: alembic.ini not found at {alembic_ini}")
        sys.exit(1)

    # Create Alembic configuration
    config = Config(str(alembic_ini))

    # Set the script location relative to alembic.ini
    config.set_main_option("script_location", str(script_dir / "migrations"))

    return config, command


def upgrade(revision="head"):
    """Upgrade database to a later version."""
    print(f"Upgrading database to {revision}...")
    config, command = run_alembic_command(["upgrade", revision])
    command.upgrade(config, revision)
    print("Upgrade completed successfully!")


def downgrade(revision="-1"):
    """Revert database to a previous version."""
    print(f"Downgrading database to {revision}...")
    config, command = run_alembic_command(["downgrade", revision])
    command.downgrade(config, revision)
    print("Downgrade completed successfully!")


def current():
    """Show current database version."""
    print("Current database version:")
    config, command = run_alembic_command(["current"])
    command.current(config, verbose=True)


def history():
    """Show migration history."""
    print("Migration history:")
    config, command = run_alembic_command(["history"])
    command.history(config, verbose=True)


def create_migration(message):
    """Create a new migration."""
    if not message:
        print("Error: Migration message is required")
        print("Usage: python migrate.py create 'Add new column'")
        sys.exit(1)

    print(f"Creating new migration: {message}")
    config, command = run_alembic_command(["revision", "-m", message])
    command.revision(config, message=message, autogenerate=True)
    print("Migration created successfully!")


def create_empty_migration(message):
    """Create an empty migration template."""
    if not message:
        print("Error: Migration message is required")
        print("Usage: python migrate.py empty 'Custom migration'")
        sys.exit(1)

    print(f"Creating empty migration: {message}")
    config, command = run_alembic_command(["revision", "-m", message])
    command.revision(config, message=message, autogenerate=False)
    print("Empty migration created successfully!")


def stamp(revision="head"):
    """Stamp database with a specific revision without running migrations."""
    print(f"Stamping database with revision {revision}...")
    config, command = run_alembic_command(["stamp", revision])
    command.stamp(config, revision)
    print("Database stamped successfully!")


def show_help():
    """Show help information."""
    help_text = """
Database Migration Helper

Commands:
  upgrade [revision]       Upgrade to a later version (default: head)
  downgrade [revision]     Downgrade to a previous version (default: -1)
  current                  Display current database version
  history                  Show migration history
  create <message>         Create auto-generated migration from model changes
  empty <message>          Create empty migration template
  stamp [revision]         Mark database as being at a specific version
  init                     Initialize database with latest schema
  reset                    Reset database (drop and recreate all tables)
  help                     Show this help message

Examples:
  python migrate.py upgrade
  python migrate.py upgrade 001
  python migrate.py downgrade
  python migrate.py downgrade base
  python migrate.py current
  python migrate.py history
  python migrate.py create "Add camera location field"
  python migrate.py stamp head

Environment Variables:
  DATABASE_URL             Full database connection URL
  DB_TYPE                  Database type: sqlite or postgresql
  DB_HOST                  PostgreSQL host (default: localhost)
  DB_PORT                  PostgreSQL port (default: 5432)
  DB_USER                  PostgreSQL user (default: postgres)
  DB_PASSWORD              PostgreSQL password
  DB_NAME                  Database name (default: ppe_detection)
  DB_PATH                  SQLite database path (default: ./data/ppe_detection.db)
"""
    print(help_text)


def init_database():
    """Initialize database with latest schema."""
    print("Initializing database...")

    # First, create tables using SQLAlchemy
    from database import init_db
    db = init_db(create_tables=True)
    print("Database tables created")

    # Then stamp with latest migration
    config, command = run_alembic_command(["stamp", "head"])
    command.stamp(config, "head")
    print("Database stamped with latest migration")

    db.close()
    print("Database initialization completed!")


def reset_database():
    """Reset database (drop and recreate all tables)."""
    response = input("WARNING: This will delete all data. Continue? (yes/no): ")

    if response.lower() != "yes":
        print("Reset cancelled")
        return

    print("Resetting database...")

    from database import Database
    db = Database()
    db.initialize()

    # Drop all tables
    print("Dropping all tables...")
    db.drop_tables()

    # Create all tables
    print("Creating all tables...")
    db.create_tables()

    # Stamp with latest migration
    config, command = run_alembic_command(["stamp", "head"])
    command.stamp(config, "head")

    db.close()
    print("Database reset completed!")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    try:
        if cmd == "upgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            upgrade(revision)

        elif cmd == "downgrade":
            revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
            downgrade(revision)

        elif cmd == "current":
            current()

        elif cmd == "history":
            history()

        elif cmd == "create":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            create_migration(message)

        elif cmd == "empty":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            create_empty_migration(message)

        elif cmd == "stamp":
            revision = sys.argv[2] if len(sys.argv) > 2 else "head"
            stamp(revision)

        elif cmd == "init":
            init_database()

        elif cmd == "reset":
            reset_database()

        elif cmd == "help":
            show_help()

        else:
            print(f"Unknown command: {cmd}")
            show_help()
            sys.exit(1)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
