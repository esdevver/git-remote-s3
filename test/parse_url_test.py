from git_remote_s3 import parse_git_url, UriScheme


def test_parse_url_trailing_slash_no_profile():
    url = "s3://bucket-name/path/to/"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket-name"
    assert profile is None
    assert prefix == "path/to"


def test_parse_url_no_profile():
    url = "s3://bucket-name/path/to"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket-name"
    assert profile is None
    assert prefix == "path/to"


def test_parse_url():
    url = "s3://profile-test@bucket-name/path/to"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket-name"
    assert profile == "profile-test"
    assert prefix == "path/to"


def test_parse_url_issue5():
    url = "s3://er@bucket/path/"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket"
    assert profile == "er"
    assert prefix == "path"


def test_parse_url_1_char_profile():
    url = "s3://A@bucket/path/"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket"
    assert profile == "A"
    assert prefix == "path"


def test_parse_url_all_supported_symbols_in_profile():
    url = "s3://Ab-tr+54_quwww@bucket/path/"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket"
    assert profile == "Ab-tr+54_quwww"
    assert prefix == "path"


def test_parse_url_unsupported_symbols_in_profile():
    url = "s3://A!@bucket/path/"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket"
    assert profile == "A!"
    assert prefix == "path"


def test_parse_url_empty_profile():
    url = "s3://@bucket/path/"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme is None
    assert bucket is None
    assert profile is None
    assert prefix is None


def test_parse_url_no_prefix_trailing_slash():
    url = "s3://profile-test@bucket-name/"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket-name"
    assert profile == "profile-test"
    assert prefix is None


def test_parse_url_no_prefix():
    url = "s3://profile-test@bucket-name"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket-name"
    assert profile == "profile-test"
    assert prefix is None


def test_parse_url_no_prefix_no_profile():
    url = "s3://bucket-name"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3
    assert bucket == "bucket-name"
    assert profile is None
    assert prefix is None


def test_parse_url_not_valid():
    url = "s4://bucket-name/path/to"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme is None
    assert bucket is None
    assert profile is None
    assert prefix is None


def test_parse_url_none():
    url = None
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme is None
    assert bucket is None
    assert profile is None
    assert prefix is None


def test_parse_url_uri_scheme_s3_zip_no_profile():
    url = "s3+zip://bucket-name/path/to"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3_ZIP
    assert bucket == "bucket-name"
    assert profile is None
    assert prefix == "path/to"


def test_parse_url_uri_scheme_s3_zip():
    url = "s3+zip://profile-test@bucket-name/path/to"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme == UriScheme.S3_ZIP
    assert bucket == "bucket-name"
    assert profile == "profile-test"
    assert prefix == "path/to"


def test_parse_url_uri_scheme_not_valid():
    url = "s3+foo://bucket-name/path/to"
    uri_scheme, profile, bucket, prefix = parse_git_url(url)
    assert uri_scheme is None
    assert bucket is None
    assert profile is None
    assert prefix is None
