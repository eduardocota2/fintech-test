"""initial schema

Revision ID: 20260409_0001
Revises: 
Create Date: 2026-04-09 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260409_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


country_code_enum = sa.Enum("MX", "CO", name="country_code")
application_status_enum = sa.Enum(
    "submitted",
    "evaluating",
    "approved",
    "rejected",
    name="application_status",
)
job_type_enum = sa.Enum("risk_evaluation", "webhook_notification", name="job_type")
job_status_enum = sa.Enum("pending", "in_progress", "completed", "failed", name="job_status")


def upgrade() -> None:
    bind = op.get_bind()
    country_code_enum.create(bind, checkfirst=True)
    application_status_enum.create(bind, checkfirst=True)
    job_type_enum.create(bind, checkfirst=True)
    job_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "loan_applications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("country", country_code_enum, nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("document_id", sa.String(length=50), nullable=False),
        sa.Column("amount_requested", sa.Numeric(12, 2), nullable=False),
        sa.Column("monthly_income", sa.Numeric(12, 2), nullable=False),
        sa.Column("application_date", sa.Date(), nullable=False),
        sa.Column("status", application_status_enum, nullable=False, server_default="submitted"),
        sa.Column("risk_rating", sa.String(length=20), nullable=True),
        sa.Column("bank_name", sa.String(length=100), nullable=True),
        sa.Column("bank_account_last4", sa.String(length=4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "job_queue",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("loan_application_id", sa.String(length=36), nullable=False),
        sa.Column("job_type", job_type_enum, nullable=False),
        sa.Column("status", job_status_enum, nullable=False, server_default="pending"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("tries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["loan_application_id"], ["loan_applications.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("loan_application_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["loan_application_id"], ["loan_applications.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_loan_country", "loan_applications", ["country"])
    op.create_index("idx_loan_status", "loan_applications", ["status"])
    op.create_index("idx_loan_created_at", "loan_applications", ["created_at"])
    op.create_index("idx_jobs_status_created", "job_queue", ["status", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_jobs_status_created", table_name="job_queue")
    op.drop_index("idx_loan_created_at", table_name="loan_applications")
    op.drop_index("idx_loan_status", table_name="loan_applications")
    op.drop_index("idx_loan_country", table_name="loan_applications")

    op.drop_table("audit_logs")
    op.drop_table("job_queue")
    op.drop_table("loan_applications")
    op.drop_table("users")

    bind = op.get_bind()
    job_status_enum.drop(bind, checkfirst=True)
    job_type_enum.drop(bind, checkfirst=True)
    application_status_enum.drop(bind, checkfirst=True)
    country_code_enum.drop(bind, checkfirst=True)
