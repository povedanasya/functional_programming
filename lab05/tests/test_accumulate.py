import operator
from itertools import accumulate, count

from streams import drop_while, prefix_products, prefix_sums, take, take_while


def test_accumulate_sum_prod() -> None:
    assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(accumulate([1, 2, 3, 4], operator.mul)) == [1, 2, 6, 24]
    assert list(prefix_sums([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(prefix_products([1, 2, 3, 4])) == [1, 2, 6, 24]


def test_accumulate_max_and_empty() -> None:
    assert list(accumulate([3, 1, 4, 1, 5], max)) == [3, 3, 4, 4, 5]
    assert list(prefix_sums([])) == []


def test_takewhile_dropwhile_on_infinite() -> None:
    assert list(take_while(lambda x: x < 5, count(1))) == [1, 2, 3, 4]
    assert take(3, drop_while(lambda x: x < 10, count(1))) == [10, 11, 12]
