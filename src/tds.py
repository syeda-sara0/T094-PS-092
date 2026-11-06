"""TDS and payouts (BR-11). Money is whole paise."""
from dataclasses import dataclass

TDS_PERCENT = 30


@dataclass
class Ledger:
    """Financial-year ledger of one user, carried from payout to payout."""
    winnings: int
    fees: int
    net_taxed: int   # cumulative net on which TDS was already deducted


@dataclass(frozen=True)
class Payout:
    contest_id: str
    user_id: str
    winnings: int
    cum_winnings: int
    cum_entry_fees: int
    cum_net: int
    taxable_increase: int
    tds: int
    net_paid: int


def round_half_up_percent(amount, percent):
    return (amount * percent + 50) // 100


def settle_user(ledger, contest_id, user_id, winnings, fees):
    """Adds this contest to the user's ledger and works out the TDS.

    TDS is only on the increase of the cumulative net over the net that was
    already taxed. While the cumulative net is negative nothing is taxed."""
    ledger.winnings += winnings
    ledger.fees += fees
    cum_net = ledger.winnings - ledger.fees
    taxable = max(cum_net - ledger.net_taxed, 0)
    tds = round_half_up_percent(taxable, TDS_PERCENT)
    if taxable > 0:
        ledger.net_taxed = cum_net
    return Payout(contest_id, user_id, winnings, ledger.winnings, ledger.fees,
                  cum_net, taxable, tds, winnings - tds)
