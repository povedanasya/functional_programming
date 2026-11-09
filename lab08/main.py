"""Демо-запуск ЛР8: журнал подій (варіант 14) і базовий приклад з виразами."""

from __future__ import annotations

from eval_ import eval_expr
from evaluator import count_errors, reduce_log, worst_level
from expr import Add, Bin, Mul, Num, Num2, eval_expr2
from model import ErrorEvent, EventGroup, FileOpened, Login, Logout
from pretty import describe


def main() -> None:
    """Друкує опис журналу, статистику reducer-а та підсумок помилок."""
    log = (
        Login("alice", 100),
        EventGroup(
            label="request-7",
            items=(
                FileOpened("alice", "/etc/config.yml", 105),
                FileOpened("alice", "/var/log/app.log", 106, mode="write"),
                EventGroup(
                    label="retry",
                    items=(
                        ErrorEvent("disk quota exceeded", "warning", 107),
                        ErrorEvent("write failed", "error", 108),
                    ),
                ),
            ),
        ),
        Login("bob", 110),
        ErrorEvent("database unreachable", "critical", 115),
        Logout("alice", 120),
    )
    for e in log:
        print(describe(e))
    print("stats:")
    for key, value in reduce_log(log).items():
        print(f"  {key}: {value}")
    print("errors >= error:", count_errors(log, min_level="error"))
    print("worst level:", worst_level(log))

    ast = Mul(Add(Num(2), Num(3)), Num(4))
    print("(2 + 3) * 4 =", eval_expr(ast))
    print("Bin:", eval_expr2(Bin("+", Num2(2), Bin("*", Num2(3), Num2(4)))))


if __name__ == "__main__":
    main()
