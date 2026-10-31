"""Read-only BSC wallet checker.

Checks BNB and ERC-20 token balances through a public BSC JSON-RPC
endpoint. This tool is read-only: it never asks for, accepts, or uses
a private key or a seed phrase. Only public wallet addresses are read.
"""
import argparse
import json
import sys

import requests

DEFAULT_RPC = "https://bsc-dataseed.binance.org/"
TRANSFER_SELECTOR = "70a08231"
NAME_SELECTOR = "06fdde03"
SYMBOL_SELECTOR = "95d89b41"
DECIMALS_SELECTOR = "313ce567"


def is_valid_address(address):
    """Return True for a 0x-prefixed 40-hex-character address."""
    if not isinstance(address, str) or not address.startswith("0x"):
        return False
    body = address[2:]
    return len(body) == 40 and all(c in "0123456789abcdefABCDEF" for c in body)


def wei_to_ether(wei):
    return wei / 10**18


def rpc_call(rpc_url, method, params):
    """Make one JSON-RPC call and return its result field."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    resp = requests.post(rpc_url, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data["result"]


def get_bnb_balance(address, rpc_url=DEFAULT_RPC):
    if not is_valid_address(address):
        raise ValueError("Invalid BSC address")
    result = rpc_call(rpc_url, "eth_getBalance", [address, "latest"])
    return wei_to_ether(int(result, 16))


def _eth_call(token, data, rpc_url):
    return rpc_call(rpc_url, "eth_call", [{"to": token, "data": data}, "latest"])


def _pad_address(address):
    return "000000000000000000000000" + address[2:].lower()


def decode_uint256(hex_data):
    return int(hex_data, 16)


def decode_string(hex_data):
    """Decode an ABI-encoded string return value."""
    raw = bytes.fromhex(hex_data[2:] if hex_data.startswith("0x") else hex_data)
    if len(raw) < 64:
        return ""
    length = int.from_bytes(raw[32:64], "big")
    return raw[64:64 + length].decode("utf-8", errors="replace")


def get_erc20_balance(token, wallet, rpc_url=DEFAULT_RPC):
    if not is_valid_address(token) or not is_valid_address(wallet):
        raise ValueError("Invalid token or wallet address")
    data = "0x" + TRANSFER_SELECTOR + _pad_address(wallet)
    result = _eth_call(token, data, rpc_url)
    raw = decode_uint256(result)
    decimals = get_erc20_decimals(token, rpc_url)
    return raw / (10 ** decimals)


def get_erc20_decimals(token, rpc_url=DEFAULT_RPC):
    result = _eth_call(token, "0x" + DECIMALS_SELECTOR, rpc_url)
    return decode_uint256(result)


def get_erc20_symbol(token, rpc_url=DEFAULT_RPC):
    result = _eth_call(token, "0x" + SYMBOL_SELECTOR, rpc_url)
    return decode_string(result)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only BSC wallet checker")
    parser.add_argument("--address", required=True, help="Public BSC wallet address")
    parser.add_argument("--rpc", default=DEFAULT_RPC, help="BSC JSON-RPC URL")
    parser.add_argument("--tokens", default="", help="Comma-separated ERC-20 token addresses")
    args = parser.parse_args(argv)
    if not is_valid_address(args.address):
        print("Invalid address", file=sys.stderr)
        return 2
    print(f"Wallet: {args.address}")
    print(f"BNB: {get_bnb_balance(args.address, args.rpc)}")
    for token in [t.strip() for t in args.tokens.split(",") if t.strip()]:
        try:
            symbol = get_erc20_symbol(token, args.rpc)
            balance = get_erc20_balance(token, args.address, args.rpc)
            print(f"{symbol or token}: {balance}")
        except Exception as exc:  # noqa: BLE001 - CLI should report, not crash
            print(f"{token}: error ({exc})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
