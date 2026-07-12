# -*- coding: utf-8 -*-
"""Foydalanuvchilar balansini oddiy JSON fayl orqali saqlash."""

import json
import os

BALANCES_FILE = os.path.join(os.path.dirname(__file__), "balances.json")


def _load() -> dict:
    if not os.path.exists(BALANCES_FILE):
        return {}
    try:
        with open(BALANCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    with open(BALANCES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_balance(user_id: int) -> int:
    data = _load()
    return int(data.get(str(user_id), 0))


def add_balance(user_id: int, amount: int) -> int:
    """Balansga qo'shadi va yangi balansni qaytaradi."""
    data = _load()
    key = str(user_id)
    data[key] = int(data.get(key, 0)) + amount
    _save(data)
    return data[key]


def deduct_balance(user_id: int, amount: int) -> int:
    """Balansdan ayiradi va yangi balansni qaytaradi. Yetarli bo'lmasa ham ayiradi -
    chaqiruvchi oldindan yetarliligini tekshirishi kerak."""
    data = _load()
    key = str(user_id)
    data[key] = int(data.get(key, 0)) - amount
    _save(data)
    return data[key]
