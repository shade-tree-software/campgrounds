D = {
1478: dict(included=4, amount=5), 1482: dict(included=2, included_children=2, amount=10),
1494: dict(included=2, amount=20, child=10, child_max_age=12), 1500: dict(included=2, included_children=3, amount=5),
1511: dict(included=2, amount=3, child=2, child_max_age=17), 1521: dict(included=4, amount=5, child=0, child_max_age=5),
1763: dict(included=2, included_children=2, amount=5), 1777: dict(included=2, amount=1),
1949: dict(included=2, amount=2), 1954: dict(included=6, amount=3), 1959: dict(included=2, amount=5),
1962: dict(included=4, amount=5, max_people=6), 1964: dict(included=3, included_children=3),
1970: dict(included=4, amount=5), 1979: dict(included=2, amount=2), 1982: dict(included=2, amount=2),
1989: dict(amount=10, max_people=12), 2012: dict(included=2, amount=10, child=0, child_max_age=9),
2017: dict(included=2, amount=5, child=0, child_max_age=17), 2034: dict(amount=10, child=0, child_max_age=5),
2036: dict(included=2, included_children=3, amount=5), 2038: dict(included=2, amount=2, child=0, child_max_age=4),
2049: dict(included=2, amount=2, child=0, child_max_age=11), 2056: dict(included=2, included_children=4, amount=5),
2063: dict(included=2, amount=5), 2073: dict(included=4, amount=5), 2078: dict(included=2, amount=3, child=0, child_max_age=1),
2213: dict(included=2, included_children=2, amount=5), 2228: dict(included=2, included_children=4, amount=10),
2233: dict(included=2, amount=2), 2308: dict(included=2),
2498: dict(amount=10, max_people=8), 2523: dict(amount=10, max_people=8), 2524: dict(included=6, amount=10, max_people=8),
2525: dict(amount=10), 2535: dict(included=6, amount=10), 2540: dict(included=6, amount=10), 2579: dict(amount=2),
}
# Every Kentucky state park note: "Base rate covers 4 adults, +$5/night per extra adult."
TEXT_RULES = [("Base rate covers 4 adults, +$5/night per extra adult.", dict(included=4, amount=5))]
REGISTRY = {"state:VT": dict(included=4, amount=8, max_people=8),
            "state:NH": dict(included=2, included_children=4, amount=10, child=5)}
SKIP_STATES = {("VT", "state"), ("NH", "state")}
