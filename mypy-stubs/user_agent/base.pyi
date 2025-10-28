from typing import (
    Union,
)

def generate_navigator(
    os: Union[None, str] = ...,
    navigator: Union[None, str] = ...,
    platform: Union[None, str] = ...,
    device_type: Union[None, str] = ...,
) -> dict[str, Union[None, str]]: ...
def generate_user_agent(
    os: Union[None, str] = ...,
    navigator: Union[None, str] = ...,
    platform: Union[None, str] = ...,
    device_type: Union[None, str] = ...,
) -> str: ...
def generate_navigator_js(
    os: Union[None, str] = ...,
    navigator: Union[None, str] = ...,
    platform: Union[None, str] = ...,
    device_type: Union[None, str] = ...,
) -> dict[str, Union[None, str]]: ...
