# usr/bin/python2.7

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import contextlib

from database_setup import Stance, Clickbait, Base

engine = create_engine('sqlite:///cnn.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# IDEA: Need to clean up the existing rows before insert the initial db rows
# only truncate the table
meta = Base.metadata

def truncate_table_all():

    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        session.execute(table.drop())
    session.commit()

def drop_table_all():
    for table in reversed(meta.sorted_tables):
        print('Drop table %s' % table)
        table.drop(engine)


if __name__ == '__main__':
    truncate_table_all()
