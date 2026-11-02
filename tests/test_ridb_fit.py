"""The Availability page's length bands: 21 ft up to the fit threshold is tight, not hidden."""
import unittest

from ridb.fetch_facility import DEFAULT_FIT_FT, TIGHT_MIN_FT, classify_fit


def site(driveway=None, cap=0, equipment="RV"):
    attrs = []
    if driveway is not None:
        attrs.append({"AttributeName": "Driveway Length", "AttributeValue": str(driveway)})
    return {"CampsiteType": "STANDARD NONELECTRIC", "ATTRIBUTES": attrs,
            "PERMITTEDEQUIPMENT": [{"EquipmentName": equipment, "MaxLength": cap}]}


class TightBand(unittest.TestCase):
    def fit(self, *args, **kw):
        return classify_fit(site(*args, **kw), DEFAULT_FIT_FT)

    def test_band_edges(self):
        self.assertEqual(TIGHT_MIN_FT, 21)
        self.assertEqual(self.fit(driveway=20.9), "too_small")
        self.assertEqual(self.fit(driveway=21), "tight")
        self.assertEqual(self.fit(driveway=24), "tight")
        self.assertEqual(self.fit(driveway=25), "fits")

    def test_lake_conasauga_posted_21_ft_on_a_long_spur_is_tight(self):
        self.assertEqual(self.fit(driveway=40, cap=21), "tight")

    def test_posted_21_ft_with_no_spur_listed_is_tight(self):
        self.assertEqual(self.fit(cap=21), "tight")

    def test_long_posted_cap_with_no_spur_listed_stays_unknown(self):
        self.assertEqual(self.fit(cap=40), "unknown")

    def test_posted_cap_under_the_band_still_hides_a_long_spur(self):
        self.assertEqual(self.fit(driveway=87, cap=10, equipment="TRAILER"), "too_small")

    def test_missing_length_stays_unknown(self):
        self.assertEqual(self.fit(), "unknown")


if __name__ == "__main__":
    unittest.main()
