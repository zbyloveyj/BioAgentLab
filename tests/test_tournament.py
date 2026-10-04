import unittest

from bioagent import ScientificSupervisor


class TournamentTests(unittest.TestCase):
    def test_returns_auditable_ranked_hypotheses(self):
        ranked, review = ScientificSupervisor().run("test question")
        self.assertEqual(len(ranked), 3)
        self.assertTrue(all(item.falsifiers for item in ranked))
        self.assertTrue(review["requires_human_review"])


if __name__ == "__main__":
    unittest.main()

