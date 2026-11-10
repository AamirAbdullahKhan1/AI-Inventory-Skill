import unittest
from src.run_manifest import ledger


class ManifestTest(unittest.TestCase):
    def test_failed_call_is_unmeasured_and_cached_is_split(self):
        base = dict(probe="example", request_sha256="synthetic", attempts=1, wall_seconds=.5)
        reported = dict(base, http_status=200, usage={
            "prompt_tokens": 20, "prompt_tokens_details": {"cached_tokens": 15},
            "completion_tokens": 6, "completion_tokens_details": {"reasoning_tokens": 2},
        })
        failed = dict(base, http_status=400)
        success, failure = ledger([reported, failed])
        self.assertEqual((success["cached_input"], success["uncached_input"],
                          success["output"], success["reasoning"]), (15, 5, 6, 2))
        self.assertIsNone(failure["output"])
