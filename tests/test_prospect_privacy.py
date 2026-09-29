import json
import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile, get_prospect


SENSITIVE_KEYS = {"tax_id", "date_of_birth", "card_on_file", "credit_check_ref"}


def keys_in_serialized(value):
    serialized = json.dumps(value)
    return {
        key for key in SENSITIVE_KEYS
        if json.dumps(key) in serialized
    }


class ProspectPrivacyTest(unittest.TestCase):
    def setUp(self):
        data_service._PROFILES.clear()

    def test_prospect_reading_tools_exclude_billing_data(self):
        prospect_id = "LEAD-18993"
        built = build_prospect_profile.invoke({"prospect_id": prospect_id})
        stored = data_service.get_profile_from_db(prospect_id)
        contact = get_prospect.invoke({"prospect_id": prospect_id})

        for result in (built, stored, contact):
            self.assertEqual(keys_in_serialized(result), set())

        self.assertNotIn("billing_qualification", built["prospect_profile"])
        self.assertNotIn("billing_qualification", stored["prospect_profile"])
        self.assertNotIn("billing_qualification", contact["prospect"])


if __name__ == "__main__":
    unittest.main()
