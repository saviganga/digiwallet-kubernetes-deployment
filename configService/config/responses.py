class CountryResponses():

    def get_supportedcountry_success(self, data):
        return {
            "status": "SUCCESS",
            "data": data
        }

    def get_country_success(self, data):
        return {
            "status": "SUCCESS",
            "data": data
        }

    def create_country_success(self, data: dict):
        return {
            "status": "SUCCESS",
            "message": "Country successfully added.",
            "data": data
        }

    def create_country_error(self, data: dict):
        return {
            "status": "FAILED",
            "message": "Unable to add country. Please check fields and try again",
            "data": data
        }

    def create_supportedcountry_success(self, data: dict):
        return {
            "status": "SUCCESS",
            "message": "supportedcountry successfully added.",
            "data": {
                "id": data.id,
                "country": data.country.country,
                "currency": data.country.currency
            }
        }

    def create_supportedcountry_error(self, data: dict):
        return {
            "status": "FAILED",
            "message": "Unable to add supported Country. Please check fields and try again.",
            "data": data
        }

    def update_country_success(self, data: dict):
        return {
            "status": "SUCCESS",
            "message": "Country successfully updated.",
            "data": data
        }

    def update_country_error(self, data: dict):
        return {
            "status": "FAILED",
            "message": "Unable to update Country. Please check fields and try again",
            "data": data
        }

    def update_supportedcountry_success(self, data: dict):
        return {
            "status": "SUCCESS",
            "message": "Country successfully updated.",
            "data": data
        }

    def update_supportedcountry_error(self, data: dict):
        return {
            "status": "FAILED",
            "message": "Unable to update supported Country. Please check fields and try again",
            "data": data
        }

country_responses = CountryResponses()
