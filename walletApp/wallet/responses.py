class WalletBoxResponses:

    def get_wallets_success(self, data: dict):
        return {
            "status": "SUCCESS",
            "data": data
        }

wallet_box_responses = WalletBoxResponses()