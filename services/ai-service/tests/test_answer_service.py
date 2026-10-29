from app.database.base import QueryResult
from app.services.answer_service import EMPTY_ANSWER, is_empty_result


def test_empty_result_detection() -> None:
    assert is_empty_result(QueryResult(columns=["a"], rows=[]))
    assert not is_empty_result(QueryResult(columns=["a"], rows=[[1]]))


def test_empty_answer_constant() -> None:
    assert "couldn't find" in EMPTY_ANSWER.lower()
