# Dependencies
import requests
import re

# API Class


class API:
    """
    Spotify API
    """

    def get_csrf_token(self):
        """
        Get a valid CSRF token from Spotify login page
        """

        # Start infinite loop
        while True:
            # Request page
            csrf_request = requests.get('https://accounts.spotify.com/')

            # On success break the loop
            if csrf_request.status_code == 200:
                break

        # Return the CSRF token
        return csrf_request.cookies.get("csrf_token")

    def login(self, csrf_token, username, password):
        """
        Login to the account using API
        Returns the token on success
        """

        # Create a session
        session = requests.session()

        # Create the payload
        payload = {
            "remember": "false",
            "username": username,
            "password": password,
            "csrf_token": csrf_token
        }

        # Create headers
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4",
            "Accept": "application/json, text/plain",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Create cookies
        cookies = {
            "csrf_token": csrf_token,
            "__bon": "MHwwfC0zMjQyMjQ0ODl8LTEzNjE3NDI4NTM4fDF8MXwxfDE="
        }

        # Execute the request
        r = session.post("https://accounts.spotify.com/api/login",
                         data=payload, headers=headers, cookies=cookies)

        # Check the response
        if "displayName" in r.text:
            return {
                "status": True,
                "msg": "working",
                "session": session
            }
        elif "errorInvalidCredentials" in r.text:
            return {
                "status": False,
                "msg": "wrong credentials"
            }
        elif "errorCSRF" in r.text:
            return {
                "status": False,
                "msg": "wrong csrf"
            }
        else:
            return {
                "status": False,
                "msg": "unknown error"
            }

    def get_account_details(self, session):
        """
        Finds account details using the session
        """

        # Get details
        while True:
            r = session.get("https://www.spotify.com/fr/account/overview/")

            if (r.ok):
                break

        # Escape unicode
        data = r.text.encode('utf-8').decode('unicode-escape')

        # Extract using regex
        plan = re.search('"plan":{"name":"(.*)","branding', data, re.IGNORECASE)

        if plan:
            plan_name = plan.group(1)

        # Extract country
        country = re.search('{"label":"Pays","value":"(.*)"}]', data, re.IGNORECASE)

        if country:
            country_code = country.group(1)

        # Extract owner
        is_owner = False
        if '''"description":"Jusqu'à six comptes Spotify Premium distincts pour des personnes''' in data:
            is_owner = True

        # Return
        return {
            "status": True,
            "country": country_code,
            "plan": plan_name,
            "is_owner": is_owner
        }