"""add asa custom columns

Revision ID: asa_custom_columns
Revises: 03ea244985ce
Create Date: 2025-01-01 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'asa_custom_columns'
down_revision = '03ea244985ce'
branch_labels = None
depends_on = None


def upgrade():
    # Add ASA custom columns to apps table
    with op.batch_alter_table('apps', schema=None) as batch_op:
        batch_op.add_column(sa.Column('asa_company_id', sa.String(length=255), nullable=True))

    # Add ASA custom columns to installed_apps table
    with op.batch_alter_table('installed_apps', schema=None) as batch_op:
        batch_op.add_column(sa.Column('asa_company_id', sa.String(length=255), nullable=True))

    # Add ASA custom columns to workflows table
    with op.batch_alter_table('workflows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('asa_company_id', sa.String(length=255), nullable=True))

    # Add ASA custom columns to app_model_configs table
    with op.batch_alter_table('app_model_configs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('asa_company_id', sa.String(length=255), nullable=True))

    # Add ASA custom columns to datasets table
    with op.batch_alter_table('datasets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('asa_company_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('asa_uid', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('access_scope', sa.String(length=255), nullable=True))


def downgrade():
    # Remove ASA custom columns from apps table
    with op.batch_alter_table('apps', schema=None) as batch_op:
        batch_op.drop_column('asa_company_id')

    # Remove ASA custom columns from installed_apps table
    with op.batch_alter_table('installed_apps', schema=None) as batch_op:
        batch_op.drop_column('asa_company_id')

    # Remove ASA custom columns from workflows table
    with op.batch_alter_table('workflows', schema=None) as batch_op:
        batch_op.drop_column('asa_company_id')

    # Remove ASA custom columns from app_model_configs table
    with op.batch_alter_table('app_model_configs', schema=None) as batch_op:
        batch_op.drop_column('asa_company_id')

    # Remove ASA custom columns from datasets table
    with op.batch_alter_table('datasets', schema=None) as batch_op:
        batch_op.drop_column('asa_company_id')
        batch_op.drop_column('asa_uid')
        batch_op.drop_column('access_scope')
