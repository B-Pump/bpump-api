from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgres://bpump_user:AcCuL4lUWY9c5prDCnwn49Cymt3rjc4Q@dpg-cn971dacn0vc738qvtag-a.frankfurt-postgres.render.com/bpump")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()