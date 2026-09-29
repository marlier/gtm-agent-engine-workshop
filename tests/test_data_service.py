import copy
import unittest

from gtm_agent import data_service


class UpdateProspectInfoTest(unittest.TestCase):
    def test_update_refreshes_source_and_cached_profile(self):
        prospect_id = "LEAD-39002"
        technology = "Terraform"
        original_stack = list(data_service.PROSPECTS[prospect_id]["tech_stack"])
        original_profile = data_service._PROFILES.get(prospect_id)
        data_service._PROFILES.clear()
        try:
            profile = copy.deepcopy(data_service.PROSPECTS[prospect_id])
            data_service.save_profile_to_db(prospect_id, profile)

            result = data_service.update_prospect_info(prospect_id, technology)

            self.assertTrue(result["updated"])
            self.assertIn(technology, data_service.fetch_tech_stack(prospect_id))
            stored_profile = data_service.get_profile_from_db(prospect_id)["prospect_profile"]
            self.assertIn(technology, stored_profile["tech_stack"])
        finally:
            data_service.PROSPECTS[prospect_id]["tech_stack"] = original_stack
            data_service._PROFILES.clear()
            if original_profile is not None:
                data_service._PROFILES[prospect_id] = original_profile
