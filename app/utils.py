from datetime import datetime, timezone

from flask import abort

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_or_404(model, object_id, description=None):
    instance = db.session.get(model, object_id)
    if instance is None:
        abort(404, description=description or f'{model.__name__} not found')
    return instance
