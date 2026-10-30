from app.services.answer_service import is_schema_inventory_question


def test_schema_inventory_question_detected() -> None:
    assert is_schema_inventory_question(
        "please give the list of all tables count and names in database schema"
    )


def test_schema_inventory_question_not_data_question() -> None:
    assert not is_schema_inventory_question("What is the price of Demo Burger?")
