"""
SQL Alchemy models for the database
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase


# class PeerInfo(BaseModel):
#     """Basic peer information"""

#     name: str
#     public_key: str
#     assigned_ip: str


# class ServerInfo(BaseModel):
#     """Server information sent to peers"""

#     public_key: str
#     endpoint: str
#     port: int
#     network_cidr: str
