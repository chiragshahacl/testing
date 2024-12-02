from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.common.database import get_db_sync_url

engine = create_engine(get_db_sync_url())
Session = scoped_session(sessionmaker(bind=engine))
