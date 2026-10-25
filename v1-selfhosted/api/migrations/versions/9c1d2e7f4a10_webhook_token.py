"""Per-user webhook token

Revision ID: 9c1d2e7f4a10
Revises: e0a4536f0db5
Create Date: 2026-10-25 20:00:00.000000

"""
import secrets

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c1d2e7f4a10'
down_revision = 'e0a4536f0db5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('webhook_token', sa.String(length=64), nullable=True))
    connection = op.get_bind()
    users = sa.table('users', sa.column('id'), sa.column('webhook_token'))
    for (user_id,) in connection.execute(sa.select([users.c.id])):
        connection.execute(users.update().where(users.c.id == user_id).values(webhook_token=secrets.token_urlsafe(32)))
    op.alter_column('users', 'webhook_token', nullable=False)


def downgrade():
    op.drop_column('users', 'webhook_token')
