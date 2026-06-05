from tare.tokenizer import Tokenizer, serialize_tool


def test_serialize_is_canonical_and_stable():
    a = serialize_tool("x", "desc", {"type": "object", "properties": {"b": {}, "a": {}}})
    b = serialize_tool("x", "desc", {"properties": {"a": {}, "b": {}}, "type": "object"})
    assert a == b  # key order independent


def test_approx_tokenizer_runs_offline():
    tok = Tokenizer("approx")
    assert not tok.is_reference
    assert tok.count("hello world") >= 1
    assert tok.label.startswith("approx")
