Daily migration workflow
1. Create a migration automatically
alembic revision --autogenerate -m "Add password changed column"
Compares your SQLAlchemy models with the database and generates a migration file.
Always review the generated file. Autogenerate may miss:
- Data migrations
- Renamed columns
- Renamed tables
- Some constraints
- Custom SQL changes
2. Apply all pending migrations
alembic upgrade head
Moves the database to the latest migration.
This is the command you use after pulling new migrations or deploying the application.
3. Check whether migrations are pending
alembic check
Returns an error if the database schema differs from the model metadata or the database is not at the latest revision.
Inspect migration state
Show the current database revision
alembic current
Shows the revision recorded in the database’s alembic_version table.
Show the latest migration
alembic heads
Shows the latest revision in your migration files.
If current and heads differ, the database is not fully upgraded.
Show migration history
alembic history
Displays the migration chain.
More detail:
alembic history --verbose
Show one specific migration
alembic show REVISION_ID
Example:
alembic show f96deed9f0c2
Show migration branches
alembic branches
Useful when multiple migration branches exist.
Upgrade and downgrade
Upgrade to the latest revision
alembic upgrade head
Upgrade by one migration
alembic upgrade +1
Upgrade to a specific revision
alembic upgrade REVISION_ID
Downgrade by one migration
alembic downgrade -1
Downgrade several migrations
alembic downgrade -2
Downgrade to a specific revision
alembic downgrade REVISION_ID
Remove all migration changes
alembic downgrade base
This returns the database to its initial empty migration state. Use carefully because it can drop tables and data.
Migration metadata commands
Mark the database as latest without running migrations
alembic stamp head
This only updates alembic_version. It does not modify tables.
Use it when an existing database already has the correct schema but Alembic does not know its revision.
Mark the database as a specific revision
alembic stamp REVISION_ID
Remove the recorded migration version
alembic stamp base
This changes migration metadata only; it does not necessarily remove database tables.
Ensure the version table exists
alembic ensure_version
Creates the alembic_version table if it does not exist.
Creating and managing migrations
Create an empty manual migration
alembic revision -m "Insert default categories"
Use this when you need custom data changes or SQL.
Example:
def upgrade() -> None:
    op.execute("INSERT INTO categories (name) VALUES ('general')")
Create a migration with autogeneration
alembic revision --autogenerate -m "Create users and todos"
This is the normal command when changing SQLAlchemy models.
Merge migration branches
alembic merge -m "Merge migration branches" REVISION_A REVISION_B
Use this when two developers created migrations from the same parent and Alembic reports multiple heads.
Edit a migration
alembic edit REVISION_ID
Opens the migration file using your configured editor.
Generate SQL without executing it
alembic upgrade head --sql
Save the SQL to a file:
alembic upgrade head --sql > migration.sql
This is useful for reviewing SQL or applying it manually in production.
You can also generate downgrade SQL:
alembic downgrade -1 --sql
Project setup commands
Initialize a new Alembic project
alembic init alembic
You generally do not need this now because your project already has an Alembic directory.
List available templates
alembic list_templates
Recommended workflow for your project
# Change a SQLAlchemy model

alembic revision --autogenerate -m "Describe the schema change"

# Review the generated migration

alembic upgrade head

# Confirm the database is current

alembic current
alembic heads
alembic check
Important: alembic revision --autogenerate creates a migration; it does not apply it. alembic upgrade head applies it. Also, Alembic uses upgrade, not migrate.


8:43 PM








what about this:
alembic revision without autogenerate flag??







8:44 PM






alembic revision -m "Add default categories"
Without --autogenerate, Alembic creates an empty migration template. It does not inspect your models or database.
Generated file:
def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
You manually add operations:
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.execute(
        "UPDATE users SET password_changed_at = created_at "
        "WHERE password_changed_at IS NULL"
    )


def downgrade() -> None:
    pass
Use a manual revision for:
- Data migrations
- Custom SQL
- Backfilling existing rows
- Renaming tables or columns
- Complex constraints or indexes
- Operations Alembic cannot detect reliably
- Stored procedures or database-specific features
Typical commands:
alembic revision -m "Backfill password timestamps"
alembic upgrade head
Comparison:
# Automatically detects model/schema changes
alembic revision --autogenerate -m "Add users table"

# Creates an empty migration for manual editing
alembic revision -m "Backfill user data"
A message is strongly recommended so the migration’s purpose is clear.