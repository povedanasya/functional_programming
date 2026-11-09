import pytest
from eval_ import EvalOverflow, eval_expr, render
from expr import Add, Bin, Mul, Num, Num2, eval_expr2


def test_eval_basic() -> None:
    assert eval_expr(Num(5)) == 5
    assert eval_expr(Add(Num(2), Num(3))) == 5
    assert eval_expr(Mul(Num(2), Num(3))) == 6


def test_eval_nested() -> None:
    ast = Mul(Add(Num(2), Num(3)), Num(4))
    assert eval_expr(ast) == 20


def test_render() -> None:
    ast = Mul(Add(Num(2), Num(3)), Num(4))
    assert render(ast) == "((2 + 3) * 4)"


def test_overflow() -> None:
    with pytest.raises(EvalOverflow):
        eval_expr(Mul(Num(1000), Num(1000)))


def test_bin_literal_form() -> None:
    assert eval_expr2(Bin("+", Num2(2), Bin("*", Num2(3), Num2(4)))) == 14
