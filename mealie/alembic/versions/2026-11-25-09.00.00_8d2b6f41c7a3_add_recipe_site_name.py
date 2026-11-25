"""add recipe site name

Revision ID: 8d2b6f41c7a3
Revises: f3a1ae61d772
Create Date: 2026-11-25 09:00:00.000000

The domain of the address a recipe was imported from. The column is nullable and is not backfilled,
so recipes created by hand and recipes imported before this revision keep no site name.

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8d2b6f41c7a3"
down_revision: str | None = "f3a1ae61d772"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.add_column("recipes", sa.Column("site_name", sa.String(), nullable=True))


def downgrade():
    op.drop_column("recipes", "site_name")
