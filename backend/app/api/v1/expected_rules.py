"""
Expected Email Rules Management API Router (v1).
Endpoints for creating, listing, and deleting monitoring rules.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.expected_rule import ExpectedEmailRule
from app.schemas.expected_rule import ExpectedRuleCreate, ExpectedRuleRead
from app.auth.security import get_current_user

router = APIRouter(prefix="/expected-rules", tags=["Expected Rules"])


@router.get("", response_model=List[ExpectedRuleRead])
def list_expected_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all active monitoring rules created by the current user.
    """
    rules = db.query(ExpectedEmailRule).filter(
        ExpectedEmailRule.user_id == current_user.id
    ).order_by(ExpectedEmailRule.created_at.desc()).all()
    return rules


@router.post("", response_model=ExpectedRuleRead, status_code=status.HTTP_201_CREATED)
def create_expected_rule(
    rule_in: ExpectedRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new Expected Email Rule for tracking (Sender email, domain, or subject keyword).
    """
    new_rule = ExpectedEmailRule(
        user_id=current_user.id,
        rule_type=rule_in.rule_type,
        rule_value=rule_in.rule_value.strip(),
        description=rule_in.description,
        is_active=True,
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return new_rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expected_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes an expected email monitoring rule by ID.
    """
    rule = db.query(ExpectedEmailRule).filter(
        ExpectedEmailRule.id == rule_id,
        ExpectedEmailRule.user_id == current_user.id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found."
        )

    db.delete(rule)
    db.commit()
    return None
