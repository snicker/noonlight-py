import aiohttp

BASE_URL = "https://api-sandbox.safetrek.io/v1"
ALARMS_URL = BASE_URL + '/alarms'
ALARM_URL = ALARMS_URL + '/{id}/status'


class NoonlightClient(object):
    """
    NoonlightClient API client

    :param token: OAuth2 token for the Noonlight API
    :type token: str
    :param session: aiohttp session to use or None
    :type session: object or None
    :param timeout: seconds to wait for before triggering a timeout
    :type timeout: integer
    """

    def __init__(self, token, session=None,
                 timeout=aiohttp.client.DEFAULT_TIMEOUT):
        """
        Creates a new :class:`NoonlightClient` instance.
        """
        self._headers = {'Authorization': "Bearer " + token,
                         'Content-Type': 'application/json'}
        if session is not None:
            self._session = session
        else:
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def get_alarm_status(self, id):
        """
        Get the status of an alarm by id

        :param id: Id of the alarm
        :returns: Alarm data as a dictionary
        :raises: ClientError, Unauthorized, BadRequest, Forbidden,
                 TooManyRequests, InternalServerError
        """
        return await self._get(ALARM_URL.format(id=id))

    async def create_alarm(self, body):
        """
        Create an alarm

        :param body: A dictionary of data to post with the alarm. Wiil be
            automatically serialized to JSON. See
            https://docs.noonlight.com/reference#create-alarm
        :returns: Alarm data as a dictionary
        :raises: ClientError, Unauthorized, BadRequest, Forbidden,
                 TooManyRequests, InternalServerError
        """
        return await self._post(ALARMS_URL, body)

    @staticmethod
    def handle_error(status, error):
        if status == 400:
            raise NoonlightClient.BadRequest(error)
        elif status == 401:
            raise NoonlightClient.Unauthorized(error)
        elif status == 403:
            raise NoonlightClient.Forbidden(error)
        elif status == 429:
            raise NoonlightClient.TooManyRequests(error)
        elif status == 500:
            raise NoonlightClient.InternalServerError(error)
        else:
            raise NoonlightClient.ClientError(error)

    async def _get(self, path, **kwargs):
        async with self._session.get(
                path, headers=dict(self._headers, **kwargs)) as resp:
            if 200 <= resp.status < 300:
                return await resp.json()
            else:
                self.handle_error(resp.status, await resp.json())

    async def _post(self, path, data, **kwargs):
        async with self._session.post(
                path, json=data, headers=dict(self._headers, **kwargs)) as resp:
            if 200 <= resp.status < 300:
                return await resp.json()
            else:
                self.handle_error(resp.status, await resp.json())

    class ClientError(Exception):
        """Generic Error."""
        pass

    class Unauthorized(ClientError):
        """Failed Authentication."""
        pass

    class BadRequest(ClientError):
        """Request is malformed."""
        pass

    class Forbidden(ClientError):
        """Access is prohibited."""
        pass

    class TooManyRequests(ClientError):
        """Too many requests for this time period."""
        pass

    class InternalServerError(ClientError):
        """Server Internal Error."""
        pass

    class InvalidData(ClientError):
        """Can't parse response data."""
        pass
