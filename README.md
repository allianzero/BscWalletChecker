# BscWalletChecker

A read-only Python command-line tool to check BNB and ERC-20 token balances on BNB Smart Chain (BSC) through a public JSON-RPC endpoint.

## Security warning

This tool is **read-only**. It never asks for, accepts, or uses a private key or a seed phrase. Only public wallet addresses are read. Never paste a private key or seed phrase into any tool, including this one.

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.9 or later.

## Usage

Check a BNB balance:

```bash
python bsc_wallet_checker.py --address 0x0000000000000000000000000000000000000000
```

Check BNB plus ERC-20 tokens:

```bash
python bsc_wallet_checker.py \
  --address 0x0000000000000000000000000000000000000000 \
  --tokens 0x55d398326f99059fF775485246999027B3197955
```

Use a different RPC endpoint:

```bash
python bsc_wallet_checker.py --address <ADDRESS> --rpc https://bsc-dataseed.binance.org/
```

## How it works

- `eth_getBalance` returns the BNB balance in wei, converted to BNB.
- `balanceOf(address)` returns an ERC-20 raw balance, divided by `10 ** decimals`.
- `symbol()` and `decimals()` are read with minimal ERC-20 ABI selectors, so no full ABI file is needed.

## Example output

```text
Wallet: 0x0000000000000000000000000000000000000000
BNB: 1.5
USDT: 100.0
```

Actual values depend on the wallet and the RPC response.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests mock the RPC responses, so they run offline and never touch a real wallet.

## Limitations

- Public RPC endpoints can rate-limit or be slow; retry or switch endpoints if needed.
- Token symbols and decimals depend on the token contract returning standard ERC-20 values.
- This tool reports balances only. It does not send transactions, sign anything, or move funds.

## License

MIT. See `LICENSE`.
