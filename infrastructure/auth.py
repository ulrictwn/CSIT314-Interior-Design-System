"""Read the basic demo login state for display; pages do not require authentication."""
from flask import g, session
from entity.accounts.user_account import UserAccount


def load_account():
    account_id = session.get('account_id')
    g.current_user = UserAccount.getUserAccount(account_id) if account_id else None
