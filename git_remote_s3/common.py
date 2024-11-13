# SPDX-FileCopyrightText: 2023-present Amazon.com, Inc. or its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import re


def parse_git_url(url: str) -> tuple[str, str, str, str]:
    """Parses the elements in an s3:// remote origin URI

    Args:
        url (str): the URI to parse

    Returns:
        tuple[str, str, str, str]: uri scheme, prefix, bucket and profile extracted
        from the URI or None, None, None, None if the URI is invalid
    """
    if url is None:
        return None, None, None, None
    m = re.match(r"(s3.*)://([^@]+@)?([a-z0-9][a-z0-9\.-]{2,62})/?(.+)?", url)
    if m is None or len(m.groups()) != 4:
        return None, None, None, None
    uri_scheme, profile, bucket, prefix = m.groups()
    if profile is not None:
        profile = profile[:-1]
    if prefix is not None:
        prefix = prefix.strip("/")
    return uri_scheme, profile, bucket, prefix
