import unittest
from unittest.mock import patch

import bsc_wallet_checker as m


class FakeResp:
    def __init__(self, result):
        self._result = result

    def raise_for_status(self):
        pass

    def json(self):
        return {"jsonrpc": "2.0", "id": 1, "result": self._result}


class TestChecker(unittest.TestCase):
    def test_valid_address(self):
        self.assertTrue(m.is_valid_address("0x" + "ab" * 20))
        self.assertFalse(m.is_valid_address("not-an-address"))
        self.assertFalse(m.is_valid_address("0x123"))

    def test_wei_to_ether(self):
        self.assertEqual(m.wei_to_ether(10**18), 1.0)

    def test_decode_string(self):
        text = "USDT"
        encoded = (32).to_bytes(32, "big") + (4).to_bytes(32, "big") + text.encode() + b"\x00" * 28
        self.assertEqual(m.decode_string("0x" + encoded.hex()), "USDT")

    @patch("bsc_wallet_checker.requests.post")
    def test_bnb_balance(self, mock_post):
        mock_post.return_value = FakeResp(hex(2 * 10**18))
        self.assertEqual(m.get_bnb_balance("0x" + "ab" * 20), 2.0)

    @patch("bsc_wallet_checker.requests.post")
    def test_erc20_balance(self, mock_post):
        # balanceOf call, then decimals call
        mock_post.side_effect = [FakeResp(hex(5000000)), FakeResp(hex(6))]
        balance = m.get_erc20_balance("0x" + "11" * 20, "0x" + "ab" * 20)
        self.assertEqual(balance, 5.0)


if __name__ == "__main__":
    unittest.main()
