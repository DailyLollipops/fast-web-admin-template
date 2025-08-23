# pyright: reportAttributeAccessIssue=false

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
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('profile', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
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
        sa.Column('modified_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    role_access_control_table = op.create_table('role_access_control',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('modified_by_id', sa.Integer(), nullable=True),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role')
    )

    templates_table = op.create_table('templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('template_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('path', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('modified_by_id', sa.Integer(), nullable=True),
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
        sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('seen', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.bulk_insert(
        application_settings_table, [
            {
                'name': 'notification',
                'value': '1',
            },
            {
                'name': 'user_verification',
                'value': 'none',
            },
            {
                'name': 'base_url',
                'value': 'http://localhost',
            },
            {
                'name': 'smtp_server',
                'value': '',
            },
            {
                'name': 'smtp_port',
                'value': '',
            },
            {
                'name': 'smtp_username',
                'value': '',
            },
            {
                'name': 'smtp_password',
                'value': '',
            },
        ]
    )

    op.bulk_insert(
        role_access_control_table, [
            {
                'role': 'system',
                'permissions': ["*"]
            },
            {
                'role': 'admin',
                'permissions': ["templates.*"]
            },
            {
                'role': 'user',
                'permissions': []
            },
        ]
    )

    op.bulk_insert(
        templates_table, [
            {
                'name': 'email_verification',
                'template_type': 'email',
                'path': 'templates/emails/email_verification.html.j2',
            },
        ]
    )



def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('application_settings')
    op.drop_table('users')
