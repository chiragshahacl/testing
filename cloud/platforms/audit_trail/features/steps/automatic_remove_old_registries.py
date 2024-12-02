from unittest.mock import patch

import yaml
from behave import step
from remove_old_registries import remove_old_entries
from tests.factories.internal_audit_factory import InternalAuditFactory

from src.common.models import InternalAudit
from src.settings import settings


@step("The MAX_REGISTRY_IN_DB setting is set to {n:d}")
def set_max_registry(context, n):
    settings.MAX_REGISTRY_IN_DB = n


@step("There are entries in InternalAudit table with the following dates")
def insert_internal_audit_entries(context):
    dates = yaml.safe_load(context.text)

    for date in dates:
        instance = InternalAuditFactory(timestamp=date)
        context.db.add(instance)
        context.db.commit()


@step("Remove old registry process is called")
def call_remove_old_registry(context):
    remove_old_entries()


@step("The only remaining entries in the InternalAudit tables have the following dates")
def check_remaining_entries(context):
    dates = yaml.safe_load(context.text)
    internal_audits = context.db.query(InternalAudit).all()

    assert len(dates) == len(internal_audits)
    for date, internal_audit in zip(dates, internal_audits):
        assert internal_audit.timestamp == date
