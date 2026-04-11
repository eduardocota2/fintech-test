"""add_terminal_status_webhook_trigger

Revision ID: 4f98f51da081
Revises: 37806d469804
Create Date: 2026-04-11 04:41:28.459395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f98f51da081'
down_revision: Union[str, Sequence[str], None] = '37806d469804'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION enqueue_terminal_webhook_job()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            generated_id text;
        BEGIN
            IF NEW.status IS DISTINCT FROM OLD.status
               AND NEW.status IN ('approved', 'rejected') THEN
                generated_id :=
                    substr(md5(random()::text || clock_timestamp()::text), 1, 8)
                    || '-'
                    || substr(md5(random()::text || clock_timestamp()::text), 1, 4)
                    || '-'
                    || substr(md5(random()::text || clock_timestamp()::text), 1, 4)
                    || '-'
                    || substr(md5(random()::text || clock_timestamp()::text), 1, 4)
                    || '-'
                    || substr(md5(random()::text || clock_timestamp()::text), 1, 12);

                INSERT INTO job_queue (
                    id,
                    loan_application_id,
                    job_type,
                    status,
                    payload,
                    tries,
                    max_retries
                )
                VALUES (
                    generated_id,
                    NEW.id,
                    'webhook_notification',
                    'pending',
                    json_build_object(
                        'application_id', NEW.id,
                        'status', NEW.status,
                        'country', NEW.country,
                        'trigger_source', 'db_trigger'
                    ),
                    0,
                    3
                );
            END IF;

            RETURN NEW;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_loan_terminal_status_webhook
        AFTER UPDATE OF status ON loan_applications
        FOR EACH ROW
        EXECUTE FUNCTION enqueue_terminal_webhook_job();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_loan_terminal_status_webhook ON loan_applications")
    op.execute("DROP FUNCTION IF EXISTS enqueue_terminal_webhook_job()")