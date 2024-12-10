"""IP address management service"""

import ipaddress
from typing import Optional
from sqlalchemy.orm import Session
from ..database.models import IPAllocation


class IPManager:
    """Service for managing IP address allocation"""

    def __init__(self, network_cidr: str, server_ip: Optional[str] = None):
        self.network = ipaddress.ip_network(network_cidr)
        self.server_ip = server_ip or str(next(self.network.hosts()))

    def initialize_ip_pool(self, db: Session) -> None:
        """Initialize IP allocation table with server IP reserved"""
        # Reserve server IP
        allocation = IPAllocation(ip_address=self.server_ip, is_reserved=True)
        db.add(allocation)
        db.commit()

    def allocate_ip(self, db: Session, peer_id: int) -> str:
        """Allocate next available IP address"""
        # Get all allocated IPs
        allocated_ips = {alloc.ip_address for alloc in db.query(IPAllocation).all()}

        # Find first available IP
        for ip in self.network.hosts():
            ip_str = str(ip)
            if ip_str not in allocated_ips:
                allocation = IPAllocation(ip_address=ip_str, peer_id=peer_id)
                db.add(allocation)
                db.commit()
                return ip_str

        raise RuntimeError("No available IP addresses")

    def release_ip(self, db: Session, peer_id: int) -> None:
        """Release IP address allocated to peer"""
        allocation = (
            db.query(IPAllocation).filter(IPAllocation.peer_id == peer_id).first()
        )
        if allocation and not allocation.is_reserved:
            db.delete(allocation)
            db.commit()

    def get_peer_ip(self, db: Session, peer_id: int) -> Optional[str]:
        """Get IP address allocated to peer"""
        allocation = (
            db.query(IPAllocation).filter(IPAllocation.peer_id == peer_id).first()
        )
        return allocation.ip_address if allocation else None
