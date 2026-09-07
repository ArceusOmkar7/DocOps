"""Unit tests for the multi-taxpayer family bundle segregation engine."""

from app.services.segregation import (
    MemberProfile,
    PageInput,
    assign_segments_to_members,
    detect_identity_signals,
    pages_from_ocr_result,
    segregate_pages,
)


def _form16_page(pan: str, name: str, tan: str = "MUMA12345B") -> str:
    return (
        f"FORM 16\n"
        f"Certificate under section 203 of the Income-tax Act\n"
        f"Name of Deductee : {name}\n"
        f"PAN of the Deductee : {pan}\n"
        f"TAN of the Payer : {tan}\n"
        f"Gross Salary : 1200000\n"
    )


def _lic_receipt_page(pan: str, name: str) -> str:
    return (
        f"LIC OF INDIA\n"
        f"Premium Receipt\n"
        f"Policyholder Name : {name}\n"
        f"PAN : {pan}\n"
        f"Premium Amount : INR 25000\n"
    )


def test_detect_identity_signals_finds_pan_tan_and_names():
    signals = detect_identity_signals(_form16_page("ABCPK1234F", "RAMESH KUMAR"))

    assert signals.pans == {"ABCPK1234F"}
    assert signals.tans == {"MUMA12345B"}
    assert any("RAMESH KUMAR" in name for name in signals.names)


def test_segregate_splits_bundle_on_changing_pan():
    pages = [
        PageInput(page_index=0, text=_form16_page("ABCPK1234F", "RAMESH KUMAR")),
        PageInput(page_index=1, text="Annexure - salary slip details for Ramesh"),  # continuation
        PageInput(page_index=2, text=_lic_receipt_page("BQDPS5678M", "SUNITA KUMAR")),
    ]

    segments = segregate_pages(pages)

    assert len(segments) == 2
    first, second = segments
    assert first.pan == "ABCPK1234F"
    assert first.page_indices == [0, 1]
    assert "salary slip" in first.text
    assert second.pan == "BQDPS5678M"
    assert second.page_indices == [2]


def test_segregate_keeps_same_pan_pages_together_even_with_new_name():
    pages = [
        PageInput(page_index=0, text=_form16_page("ABCPK1234F", "RAMESH KUMAR", tan="DELE09876A")),
        PageInput(
            page_index=1,
            text=_form16_page("ABCPK1234F", "RAMESH KUMAR", tan="MUMA12345B"),
        ),
    ]

    segments = segregate_pages(pages)

    # Different TAN but same PAN keeps them in one segment (same taxpayer).
    assert len(segments) == 1
    assert segments[0].page_indices == [0, 1]


def test_segregate_leading_blank_pages_own_a_segment():
    pages = [
        PageInput(page_index=0, text="Scan cover page"),
        PageInput(page_index=1, text=_form16_page("ABCPK1234F", "RAMESH KUMAR")),
    ]

    segments = segregate_pages(pages)

    assert len(segments) == 2
    assert segments[0].page_indices == [0]
    assert segments[1].page_indices == [1]


def test_assign_by_exact_pan():
    segments = segregate_pages(
        [
            PageInput(page_index=0, text=_form16_page("ABCPK1234F", "RAMESH KUMAR")),
            PageInput(page_index=1, text=_lic_receipt_page("BQDPS5678M", "SUNITA KUMAR")),
        ]
    )
    members = [
        MemberProfile(member_id="m-1", name="Ramesh Kumar", pan="ABCPK1234F"),
        MemberProfile(member_id="m-2", name="Sunita Kumar", pan="BQDPS5678M"),
    ]

    assignments = assign_segments_to_members(segments, members)

    by_member = {a.member_id: a for a in assignments}
    assert set(by_member) == {"m-1", "m-2"}
    assert all(a.matched_by == "pan" for a in assignments)
    assert by_member["m-1"].segment.pan == "ABCPK1234F"


def test_assign_by_name_when_segment_has_no_pan():
    pages = [
        PageInput(
            page_index=0,
            text="Name of Deductee : Sunita Kumar\nInterest Certificate\n",
        )
    ]
    segments = segregate_pages(pages)
    members = [MemberProfile(member_id="m-2", name="Sunita Kumar", pan=None)]

    assignments = assign_segments_to_members(segments, members)

    assert len(assignments) == 1
    assert assignments[0].member_id == "m-2"
    assert assignments[0].matched_by == "name"


def test_unmatched_segments_are_omitted():
    segments = segregate_pages(
        [PageInput(page_index=0, text=_form16_page("ZZZPZ9999Z", "UNKNOWN PERSON"))]
    )
    members = [MemberProfile(member_id="m-1", name="Ramesh Kumar", pan="ABCPK1234F")]

    assignments = assign_segments_to_members(segments, members)

    assert assignments == []


def test_pages_from_ocr_result_uses_block_text_fallback():
    result = {
        "pages": [
            {
                "page_index": 0,
                "text": "",
                "blocks": [{"text": "PAN : ABCPK1234F"}, {"text": "Gross Salary"}],
            }
        ]
    }

    pages = pages_from_ocr_result(result)

    assert len(pages) == 1
    assert "ABCPK1234F" in pages[0].text
    signals = detect_identity_signals(pages[0].text)
    assert signals.pans == {"ABCPK1234F"}
