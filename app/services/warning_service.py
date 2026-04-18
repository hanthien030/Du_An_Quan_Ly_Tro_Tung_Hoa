from app.extensions import db
from app.models import HopDong


def update_all_hop_dong_status():
    """Sync contract and room statuses using Rule 3 and Rule 4."""
    contracts = HopDong.query.all()
    changed = False

    for contract in contracts:
        old_status = contract.trang_thai
        old_room_status = contract.phong.trang_thai if contract.phong else None
        contract.update_trang_thai()
        new_room_status = contract.phong.trang_thai if contract.phong else None
        if contract.trang_thai != old_status or new_room_status != old_room_status:
            changed = True

    if changed:
        db.session.commit()

    return contracts


def get_sap_het_han(days=30):
    contracts = update_all_hop_dong_status()
    return [
        contract for contract in contracts
        if contract.trang_thai == 'sap_het_han'
        and contract.days_remaining() is not None
        and contract.days_remaining() <= days
    ]
