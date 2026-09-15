import pytest
from pydantic import ValidationError
from app.schemas.schemas import ReviewIn
def test_rating_is_constrained_to_one_through_five():
    with pytest.raises(ValidationError): ReviewIn(order_id=1,rating=0,title="Bad",comment="Too short? no, this is long enough")
    assert ReviewIn(order_id=1,rating=5,title="Excellent",comment="Comfortable and well made.").rating==5
