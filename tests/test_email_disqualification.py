import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent.gtm_agent import SYSTEM_PROMPT, send_prospect_email


class EmailDisqualificationTest(unittest.TestCase):
    def test_disqualified_prospect_email_is_sent_with_warning(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "name": "Priya Nair",
                "email": "priya.nair@example.com",
                "disqualified": True,
            },
            "Following up",
            "Hello Priya,",
            runtime=None,
            from_rep={"name": "Alex Rep", "email": "alex@example.com"},
        )

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["warnings"], ["disqualified"])

    def test_email_prompt_requires_disqualified_disclosure(self):
        self.assertIn("do not refuse or delay the send", SYSTEM_PROMPT)
        self.assertIn("true disqualified flag", SYSTEM_PROMPT)
        self.assertIn("confirmation message", SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
