from core.classify import PageClass
from core.classify import PageKind
from core.classify import classify_pages


def test_classify_digital_above_threshold():
    result = classify_pages([(0, 250)])
    assert result == [PageClass(index=0, kind=PageKind.digital)]


def test_classify_scanned_below_threshold():
    result = classify_pages([(0, 10), (1, 300)])
    assert result == [
        PageClass(index=0, kind=PageKind.scanned),
        PageClass(index=1, kind=PageKind.digital),
    ]


def test_classify_empty():
    assert classify_pages([]) == []
