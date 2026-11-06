import os
import sys
from decimal import Decimal

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from loader import Delivery, Player  # noqa: E402


def ball(striker="S", bowler="B", runs=0, extras="", extras_runs=0, wicket="",
         out="", f1="", f2="", direct=False, over=0, seq=1, innings=1):
    """One delivery with sensible defaults, for small tests."""
    return Delivery("MT-X", innings, over, seq, striker, bowler, runs, extras,
                    extras_runs, wicket, out, f1, f2, direct)


def player(pid, team, role, credits):
    return Player(pid, "Name " + pid, team, role, Decimal(credits))
