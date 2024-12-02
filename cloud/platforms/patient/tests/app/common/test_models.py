from datetime import date

import pytest
from features.factories.patient_factories import PatientFactory
from sqlalchemy import text

from app.settings import config


@pytest.mark.asyncio
async def test_process_patient_pii_encryption(async_db_session):
    patient = PatientFactory.build(
        given_name="Alf",
        family_name="House Pippo",
        birth_date=date(year=2015, month=12, day=15),
    )
    async_db_session.add(patient)
    await async_db_session.flush()

    stmt = text("SELECT given_name, family_name, birth_date FROM patients")

    result = await async_db_session.execute(stmt)

    given_name, family_name, birth_date = result.all()[0]
    assert given_name != "Alf"
    assert family_name != "House Pippo"
    assert birth_date != "2015-12-15"

    stmt = text(
        f"""
        SELECT
            pgp_sym_decrypt(given_name, '{config.DB_ENCRYPTION_KEY.get_secret_value()}'),
            pgp_sym_decrypt(family_name, '{config.DB_ENCRYPTION_KEY.get_secret_value()}'),
            pgp_sym_decrypt(birth_date, '{config.DB_ENCRYPTION_KEY.get_secret_value()}')
        FROM patients;
        """
    )
    result = await async_db_session.execute(stmt)
    given_name, family_name, birth_date = result.all()[0]
    assert given_name == "Alf"
    assert family_name == "House Pippo"
    assert birth_date == "2015-12-15"
