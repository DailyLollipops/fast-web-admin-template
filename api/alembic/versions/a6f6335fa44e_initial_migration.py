"""Initial migration

Revision ID: a6f6335fa44e
Revises: 
Create Date: 2025-01-09 16:18:30.806076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import bcrypt


# revision identifiers, used by Alembic.
revision: str = 'a6f6335fa44e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users_table = op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False),
        sa.Column('api', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    application_settings_table = op.create_table('application_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('value', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('modified_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    templates_table = op.create_table('templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('template_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('path', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('modified_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('triggered_by', sa.Integer(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('body', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('seen', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.bulk_insert(
        users_table, [
            {
                'name': 'System',
                'email': 'system@example.com',
                'role': 'system',
                'password': bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                'verified': True
            }
        ]
    )

    op.bulk_insert(
        application_settings_table, [
            {
                'name': 'notification',
                'value': '1',
                'modified_by_id': 1
            },
            {
                'name': 'user_verification',
                'value': 'none',
                'modified_by_id': 1
            },
            {
                'name': 'base_url',
                'value': 'http://localhost',
                'modified_by_id': 1
            },
            {
                'name': 'smtp_server',
                'value': '',
                'modified_by_id': 1
            },
            {
                'name': 'smtp_port',
                'value': '',
                'modified_by_id': 1
            },
            {
                'name': 'smtp_username',
                'value': '',
                'modified_by_id': 1
            },
            {
                'name': 'smtp_password',
                'value': '',
                'modified_by_id': 1
            },
        ]
    )

    op.bulk_insert(
        templates_table, [
            {
                'name': 'email_verification',
                'template_type': 'email',
                'path': 'templates/emails/email_verification.html.j2',
                'modified_by_id': 1,
            },
        ]
    )



def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('application_settings')
    op.drop_table('users')
