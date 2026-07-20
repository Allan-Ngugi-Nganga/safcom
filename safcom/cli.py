"""Command-line interface for safcom."""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="safcom",
        description="M-Pesa toolkit from the terminal",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── stkpush ──
    stk = sub.add_parser("stkpush", help="Send an STK push to a phone")
    stk.add_argument("phone", help="Phone number (e.g. 254712345678)")
    stk.add_argument("amount", type=int, help="Amount to charge")
    stk.add_argument("--ref", default="INV-001", help="Account reference")
    stk.add_argument("--desc", help="Transaction description")
    stk.add_argument("--callback", help="Callback URL")
    stk.add_argument("--key", help="Consumer key (or SAFCOM_CONSUMER_KEY)")
    stk.add_argument("--secret", help="Consumer secret (or SAFCOM_CONSUMER_SECRET)")
    stk.add_argument("--passkey", help="Passkey (or SAFCOM_PASSKEY)")
    stk.add_argument("--shortcode", help="Shortcode (or SAFCOM_SHORTCODE)")
    stk.add_argument("--env", choices=["sandbox", "production"], default="sandbox")

    # ── query ──
    q = sub.add_parser("query", help="Query STK push status")
    q.add_argument("checkout_id", help="CheckoutRequestID from stkpush")
    q.add_argument("--key", help="Consumer key (or SAFCOM_CONSUMER_KEY)")
    q.add_argument("--secret", help="Consumer secret (or SAFCOM_CONSUMER_SECRET)")
    q.add_argument("--passkey", help="Passkey (or SAFCOM_PASSKEY)")
    q.add_argument("--shortcode", help="Shortcode (or SAFCOM_SHORTCODE)")
    q.add_argument("--env", choices=["sandbox", "production"], default="sandbox")

    args = parser.parse_args()

    # Credentials from args or env vars
    consumer_key = args.key or os.environ.get("SAFCOM_CONSUMER_KEY")
    consumer_secret = args.secret or os.environ.get("SAFCOM_CONSUMER_SECRET")
    passkey = args.passkey or os.environ.get("SAFCOM_PASSKEY")
    shortcode = args.shortcode or os.environ.get("SAFCOM_SHORTCODE")

    missing = []
    if not consumer_key:
        missing.append("consumer key")
    if not consumer_secret:
        missing.append("consumer secret")
    if not passkey:
        missing.append("passkey")
    if not shortcode:
        missing.append("shortcode")
    if missing:
        print(f"Error: Missing {', '.join(missing)}. Provide via --flags or environment variables.")
        sys.exit(1)

    from safcom import Mpesa

    mpesa = Mpesa(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        passkey=passkey,
        shortcode=shortcode,
        env=args.env,
    )

    if args.command == "stkpush":
        if args.callback:
            mpesa.set_callback_url(args.callback)
        resp = mpesa.stk_push(
            phone=args.phone,
            amount=args.amount,
            account_ref=args.ref,
            transaction_desc=args.desc,
        )
        print(f"✅ STK push sent!")
        print(f"   CheckoutRequestID: {resp.checkout_request_id}")
        print(f"   Message: {resp.customer_message}")

    elif args.command == "query":
        status = mpesa.stk_push_query(args.checkout_id)
        print(f"Status: {'✅ Paid' if status.success else '❌ ' + (status.result_description or 'Pending')}")
        if status.receipt:
            print(f"   Receipt: {status.receipt}")
        if status.amount:
            print(f"   Amount: KES {status.amount}")
        if status.phone:
            print(f"   Phone: {status.phone}")


if __name__ == "__main__":
    main()
