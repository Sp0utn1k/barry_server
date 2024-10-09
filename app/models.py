from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

Base = declarative_base()
engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)
session = Session()

class Alarm(Base):
    __tablename__ = 'alarms'
    id = Column(String, primary_key=True)
    time = Column(String)  # Use appropriate datetime type
    repeat = Column(String)
    duration = Column(Integer)
    sequence_id = Column(String)

    def __init__(self, time, repeat, duration, sequence_id):
        self.id = str(uuid.uuid4())
        self.time = time
        self.repeat = repeat
        self.duration = duration
        self.sequence_id = sequence_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            time=data['time'],
            repeat=data.get('repeat', 'none'),
            duration=data['duration'],
            sequence_id=data['sequence_id']
        )

    def save(self):
        session.add(self)
        session.commit()

class Sequence(Base):
    __tablename__ = 'sequences'
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    waypoints = Column(JSON)

    def __init__(self, name, waypoints):
        self.id = str(uuid.uuid4())
        self.name = name
        self.waypoints = waypoints

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            waypoints=data['waypoints']
        )

    def save(self):
        session.add(self)
        session.commit()

# Create tables
Base.metadata.create_all(engine)
