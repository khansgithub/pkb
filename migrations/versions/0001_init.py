"""init documents + snippets

Revision ID: 0001_init
Revises: 
Create Date: 2026-01-20

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("path", name="uq_documents_path"),
    )

    op.create_table(
        "snippets",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("document_id", sa.BigInteger(), nullable=False),
        sa.Column("snippet_hash", sa.String(length=64), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("heading_path", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=64), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column(
            "tsv",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector('english', "
                "coalesce(title,'') || ' ' || coalesce(heading_path,'') || ' ' || "
                "coalesce(language,'') || ' ' || coalesce(code,''))",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name="fk_snippets_document_id_documents",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "document_id", "snippet_hash", name="uq_snippets_doc_hash"
        ),
    )

    op.create_index("ix_snippets_document_id", "snippets", ["document_id"])
    op.create_index("ix_snippets_language", "snippets", ["language"])
    op.create_index("ix_snippets_tsv", "snippets", ["tsv"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_index("ix_snippets_tsv", table_name="snippets")
    op.drop_index("ix_snippets_language", table_name="snippets")
    op.drop_index("ix_snippets_document_id", table_name="snippets")
    op.drop_table("snippets")
    op.drop_table("documents")

