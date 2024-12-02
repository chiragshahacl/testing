from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.common.database import get_db_sync_url
from src.settings import settings


def remove_old_entries():
    # Create the SQLAlchemy engine and session
    DATABASE_URL = get_db_sync_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        delete_query = text(
            f"""
                DELETE FROM internal_audit
                WHERE id NOT IN (
                    SELECT id
                    FROM internal_audit
                    ORDER BY timestamp DESC
                    LIMIT {settings.MAX_REGISTRY_IN_DB}
                )
            """
        )
        session.execute(delete_query)
        session.commit()

        logger.info(
            f"Deleted excess entries, keeping the {settings.MAX_REGISTRY_IN_DB} newest entries."
        )
    except Exception:
        session.rollback()
        logger.exception("Error deleting entries")
    finally:
        logger.info("Closing session...")
        session.close()


if __name__ == "__main__":
    remove_old_entries()
    exit(0)
