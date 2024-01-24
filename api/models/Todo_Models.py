# class Source(Base):
#     __tablename__ = "sources"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50))
#     location = Column(String(50))
#     timeCreated = Column(DateTime(timezone=AppConfig.db_useTimeZone), server_default=func.now())
#     timeUpdated = Column(DateTime(timezone=AppConfig.db_useTimeZone), onupdate=func.now())

# class ActionSchedule(Base):
#     __tablename__ = "action_schedules"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50))
#     cronmask = Column(String(50))

# class ActionType(Base):
#     __tablename__ = "action_types"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50))
#     type = Column(String(50))  # trigger, cron
#     # startTime = Column(DateTime(timezone=AppConfig.db_useTimeZone))
#     cronmask = Column(String(50))
#     # action_schedule_id = Column(Integer, ForeignKey('action_schedules.id'), nullable=True)
