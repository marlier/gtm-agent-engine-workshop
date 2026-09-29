import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import gtm_agent


class ScoreProspectTests(unittest.TestCase):
    def setUp(self):
        self.prospect_profile = {
            "annual_revenue": 10_000_000,
            "industry": "Technology",
            "tech_stack": ["Snowflake", "dbt"],
        }
        self.offering = {
            "description": "Data platform",
            "min_annual_revenue": 1_000_000,
            "required_tech_stack": ["Snowflake", "Looker", "dbt", "Fivetran"],
        }

    def test_identical_inputs_return_identical_scores(self):
        llm = Mock()
        llm.invoke.return_value = gtm_agent.ProspectJudgement(
            revenue_fit=80,
            segment_fit=60,
            justification="Good revenue and segment fit.",
        )
        with patch.object(gtm_agent, "_scoring_llm", llm):
            first = gtm_agent.score_prospect.invoke({
                "prospect_profile": self.prospect_profile,
                "offering": self.offering,
            })
            second = gtm_agent.score_prospect.invoke({
                "prospect_profile": self.prospect_profile,
                "offering": self.offering,
            })

        self.assertEqual(first["score"], second["score"])

    def test_score_matches_documented_rubric_weights(self):
        llm = Mock()
        llm.invoke.return_value = gtm_agent.ProspectJudgement(
            revenue_fit=80,
            segment_fit=60,
            justification="Good revenue and segment fit.",
        )
        with patch.object(gtm_agent, "_scoring_llm", llm):
            result = gtm_agent.score_prospect.invoke({
                "prospect_profile": self.prospect_profile,
                "offering": self.offering,
            })

        rubric = result["rubric_breakdown"]
        expected = sum(
            rubric[component] * weight
            for component, weight in gtm_agent.SCORE_WEIGHTS.items()
        )
        self.assertEqual(result["score"], expected)
        self.assertEqual(rubric["tech_stack_match"], 50.0)

    def test_out_of_range_component_is_rejected(self):
        llm = Mock()
        llm.invoke.return_value = {
            "revenue_fit": 101,
            "segment_fit": 60,
            "justification": "Invalid revenue fit.",
        }
        with patch.object(gtm_agent, "_scoring_llm", llm):
            with self.assertRaises(ValueError):
                gtm_agent.score_prospect.invoke({
                    "prospect_profile": self.prospect_profile,
                    "offering": self.offering,
                })


if __name__ == "__main__":
    unittest.main()
