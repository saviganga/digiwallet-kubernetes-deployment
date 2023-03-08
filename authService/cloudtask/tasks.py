import requests
import json

from celery import shared_task

@shared_task
def create_user_wallet_signup(user, jwt_token, currency):

    # walletbox
    try:
        wallet_box_payload = {
            "user": user
        }

        wallet_box_url = "http://localhost:30004/wallet/walletbox/"

        HEADERS = {
            "Authorization": f"JWT {jwt_token}",
            "Content-Type": "application/json"
        }

        try:
            resp = requests.post(url=wallet_box_url, data=json.dumps(wallet_box_payload), headers=HEADERS)
            if resp.status_code == 201:
                wbox = resp.json()
            elif resp.status_code in range[399, 499]:
                return False, resp.json()
            else:
                return False, resp.json()
        except Exception as wberror:
            print(wberror)
            return False, 'walletbox request error'
    except Exception as wboxerror:
        print(wboxerror)
        return False, "walletbox error"

    # wallet
    try:
        wallet_payload = {
            "walletBox": wbox.get('data').get('id'),
            "currency": currency
        }

        wallet_url = "http://localhost:30004/wallet/wallets/"

        headers = {
            "Authorization": f"JWT {jwt_token}",
            "Content-Type": "application/json"
        }

        try:
            resp = requests.post(url=wallet_url, data=json.dumps(wallet_payload), headers=headers)
            if resp.status_code == 201:
                wallett = resp.json()
            elif resp.status_code == 400:
                return False, resp.json()
            else:
                return False, "Server error"
        except Exception as wberror:
            print(wberror)
            return False, 'wallet request error'
    except Exception as wboxerror:
        print(wboxerror)
        return False, "wallet error"

    return True, "created"


