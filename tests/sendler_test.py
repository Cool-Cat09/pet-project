import pytest
from sendler import send_message, SendlerResponse, sendler_settings


async def test_send_message():
    res = await send_message(msg=SendlerResponse(status='fell', email=sendler_settings.sendler_email))


    assert isinstance(res, SendlerResponse)