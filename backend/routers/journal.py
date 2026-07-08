from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.journal import JournalService

router = APIRouter(prefix="/api/journal", tags=["journal"])
journal_svc = JournalService()


class JournalEntry(BaseModel):
    date: str
    action: str
    asset: str
    amount: Optional[str] = ""
    cost: Optional[str] = ""
    reason: Optional[str] = ""


@router.get("")
def list_entries():
    return journal_svc.list_entries()


@router.post("")
def add_entry(body: JournalEntry):
    entry_id = journal_svc.add_entry(
        date=body.date,
        action=body.action,
        asset=body.asset,
        amount=body.amount,
        cost=body.cost,
        reason=body.reason,
    )
    return {"id": entry_id}
