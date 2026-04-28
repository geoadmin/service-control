from decimal import Decimal

from distributions.export_models import BaseModelWithDynamoDBSerialization


def test_base_model_with_dynamo_db_serialization():

    class MyModel(BaseModelWithDynamoDBSerialization):
        string: str
        number_int: Decimal
        number_float: Decimal
        list: list
        map: dict
        null: None
        bool_true: bool
        bool_false: bool

    model = MyModel(
        string="value",
        number_int=Decimal(10),
        number_float=Decimal("10.1"),
        list=["value"],
        map={"key": "value"},
        null=None,
        bool_true=True,
        bool_false=False,
    )
    item = model.as_dynamodb_item()

    assert item == {
        "string": {
            "S": "value"
        },
        "number_int": {
            "N": "10"
        },
        "number_float": {
            "N": "10.1"
        },
        "list": {
            "L": [{
                "S": "value"
            }]
        },
        "map": {
            "M": {
                "key": {
                    "S": "value"
                }
            }
        },
        "null": {
            "NULL": True
        },
        "bool_true": {
            "BOOL": True
        },
        "bool_false": {
            "BOOL": False
        },
    }
