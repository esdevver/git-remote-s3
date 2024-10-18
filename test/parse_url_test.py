from git_remote_s3 import parse_git_url


def test_parse_url_trailing_slash_no_profile():
    url = "s3://bucket-name/path/to/"
    profile, bucket, prefix = parse_git_url(url)
    assert bucket == "bucket-name"
    assert profile is None
    assert prefix == "path/to"


def test_parse_url_no_profile():
    url = "s3://bucket-name/path/to"
    profile, bucket, prefix = parse_git_url(url)
    assert bucket == "bucket-name"
    assert profile is None
    assert prefix == "path/to"


def test_parse_url():
    url = "s3://profile-test@bucket-name/path/to"
    profile, bucket, prefix = parse_git_url(url)
    assert bucket == "bucket-name"
    assert profile == "profile-test"
    assert prefix == "path/to"


def test_parse_url_no_prefix_trailing_slash():
    url = "s3://profile-test@bucket-name/"
    profile, bucket, prefix = parse_git_url(url)
    assert bucket == "bucket-name"
    assert profile == "profile-test"
    assert prefix is None


def test_parse_url_no_prefix():
    url = "s3://profile-test@bucket-name"
    profile, bucket, prefix = parse_git_url(url)
    assert bucket == "bucket-name"
    assert profile == "profile-test"
    assert prefix is None


def test_parse_url_no_prefix_no_profile():
    url = "s3://bucket-name"
    profile, bucket, prefix = parse_git_url(url)
    assert bucket == "bucket-name"
    assert profile is None
    assert prefix is None


def test_parse_url_not_valid():
    url = "s4://bucket-name/path/to"
    profile, bucket, prefix = parse_git_url(url)
    assert bucket is None
    assert profile is None
    assert prefix is None


def test_parse_url_none():
    url = None
    profile, bucket, prefix = parse_git_url(url)
    assert bucket is None
    assert profile is None
    assert prefix is None
