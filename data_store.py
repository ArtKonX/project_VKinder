import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine, MetaData
from config import db_url_object
import psycopg2

metadata = MetaData()
Base = declarative_base()

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS matches (
        profile_id INTEGER, 
        worksheet_id INTEGER,
        PRIMARY KEY (profile_id, worksheet_id)
        );
        """)
        conn.commit()


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()

def check_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.profile_id == profile_id,
            Viewed.worksheet_id == worksheet_id
        ).first()
        return True if from_bd else False


if __name__ == '__main__':
    with psycopg2.connect(database="postgres", user="postgres", password="") as conn:
        create_db(conn)
    conn.close()
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    add_user(engine, , )
    res = check_user(engine, , )
    print(res)