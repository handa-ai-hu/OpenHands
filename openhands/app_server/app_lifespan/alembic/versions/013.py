"""Add execution_status column to conversation_metadata

Revision ID: 013
Revises: 012
Create Date: 2026-06-16 00:00:00.000000
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '013'
down_revision: str | None = '012'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add execution_status column to conversation_metadata table.

    This column stores the current execution status of conversations
    (idle, running, paused, finished, error, stuck, deleting) for
    org-wide dashboard queries without requiring agent server calls.
    """
    import sqlalchemy as sa
    from alembic import context

    # Check if column already exists (model may have created it)
    bind = context.get_bind()
    inspector = sa.inspect(bind)
    columns = {col['name'] for col in inspector.get_columns('conversation_metadata')}

    if 'execution_status' not in columns:
        with op.batch_alter_table('conversation_metadata') as batch_op:
            batch_op.add_column(
                sa.Column(
                    'execution_status',
                    sa.String(),
                    nullable=True,
                )
            )

    # Create index if not exists
    indexes = {idx['name'] for idx in inspector.get_indexes('conversation_metadata')}
    if 'ix_conversation_metadata_execution_status' not in indexes:
        with op.batch_alter_table('conversation_metadata') as batch_op:
            batch_op.create_index(
                'ix_conversation_metadata_execution_status',
                ['execution_status'],
                unique=False,
            )


def downgrade() -> None:
    with op.batch_alter_table('conversation_metadata') as batch_op:
        batch_op.drop_index('ix_conversation_metadata_execution_status')
        batch_op.drop_column('execution_status')
