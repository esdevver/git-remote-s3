
import sys
import logging
import boto3
import re
import tempfile
import os
from . import git

s3 = boto3.client("s3")

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr)
logger.setLevel(logging.ERROR)
logger.debug(sys.argv)

remote = sys.argv[2]
origin = sys.argv[1]
bucket, prefix = re.match(r"s3://([a-z0-9][a-z0-9\.-]{2,62})(/.*)?", remote).groups()


def list_refs(*, bucket: str, prefix: str) -> list:
    res = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    contents = res.get("Contents", [])
    next_token = res.get("NextContinuationToken", None)

    while next_token:
        res = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, ContinuationToken=next_token)
        contents.extend(res.get("Contents", []))
        next_token = res.get("NextContinuationToken", None)

    contents = s3.list_objects_v2(Bucket=bucket, Prefix=prefix).get("Contents", [])
    contents.sort(key=lambda x: x["LastModified"])
    contents.reverse()

    objs = [
        o["Key"][o["Key"].index("/") + 1 :]
        for o in contents
        if o["Key"].startswith(prefix+"/")
    ]
    return objs

def cmd_fetch(args: str):
    sha, ref = args.split(" ")[1:]
    logger.debug(f"fetch {sha} {ref}")
    obj = s3.get_object(Bucket=bucket, Key=f"{prefix}/{ref}/{sha}.bundle")
    data = obj["Body"].read()
    temp_dir = tempfile.mkdtemp(prefix="git_remote_s3_fetch_")
    with open(f"{temp_dir}/{sha}.bundle", "wb") as f:
        f.write(data)
    logger.debug(f"fetched {temp_dir}/{sha}.bundle {ref}")
    git.unbundle(folder=temp_dir, sha=sha, ref=ref)


def cmd_push(args: str):
    local_ref, remote_ref = args.split(" ")[1].split(":")
    logger.debug(f"push {local_ref} {remote_ref}")
    temp_dir = tempfile.mkdtemp(prefix="git_remote_s3_push_")
    contents = s3.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/{remote_ref}").get(
        "Contents", []
    )
    if len(contents) > 1:
        sys.stderr.write(f"fatal: multiple {remote_ref} already exists on server\n")
        sys.stderr.flush()
        return
    remote_to_remove = contents[0]["Key"] if len(contents) == 1 else None
    try:
        sha = git.rev_parse(local_ref)
        git.bundle(folder=temp_dir, sha=sha, ref=local_ref)
        
        with open(f"{temp_dir}/{sha}.bundle", "rb") as f:
            s3.put_object(Bucket=bucket, Key=f"{prefix}/{remote_ref}/{sha}.bundle", Body=f)
        logger.debug(f"pushed {temp_dir}/{sha}.bundle to {remote_ref}")
        s3.delete_object(Bucket=bucket, Key=remote_to_remove) if remote_to_remove else None
        sys.stdout.write(f"ok {remote_ref}\n")
        sys.stdout.flush()
    except git.GitError: 
        sys.stderr.write(f"fatal: {local_ref} not found\n")
        sys.stderr.flush()
        return
    
def cmd_option(arg: str):
    option, value = arg.split(" ")[1:]
    if option == "verbosity" and int(value) >= 2:
        logger.setLevel(logging.DEBUG)
        sys.stdout.write("ok\n")
    else:
        sys.stdout.write("unsupported\n")
    sys.stdout.flush()


def cmd_list(for_push: bool = False):
    objs = list_refs(bucket=bucket, prefix=prefix)
    logger.debug(objs)
    if not for_push:
        for o in objs:
            if o.startswith("refs/heads/main"):
                sys.stdout.write("@refs/heads/main HEAD\n")
            if o.startswith("refs/heads/master"):
                sys.stdout.write("@refs/heads/master HEAD\n")

    for o in objs:
        elements = o.split("/")
        sha = elements[-1].split(".")[0]
        sys.stdout.write(f"{sha} {'/'.join(elements[:-1])}\n")

    sys.stdout.write("\n")
    sys.stdout.flush()


def cmd_capabilities():
    sys.stdout.write("*push\n")
    sys.stdout.write("*fetch\n")
    sys.stdout.write("option\n")
    sys.stdout.write("\n")
    sys.stdout.flush()

def main():
    if bucket is None:
        sys.stderr.write(f"fatal: invalid remote '{remote}'\n")
        sys.exit(1)

    logger.debug(f"b:{bucket} p:{prefix}")
    if prefix is not None:
        prefix = prefix[1:].strip("/")

    try:
        while True:
            l = sys.stdin.readline()
            if len(l) == 0:
                break
            logger.debug(f"cmd: {l}")
            if l.startswith("capabilities"):
                cmd_capabilities()
                continue
            if l.startswith("list for-push"):
                cmd_list(for_push=True)
                continue
            if l.startswith("list"):
                cmd_list()
                continue
            if l.startswith("fetch"):
                cmd_fetch(l.strip())
                continue
            if l.startswith("push"):
                cmd_push(l.strip())
                continue
            if l.startswith("option"):
                cmd_option(l.strip())
                continue
            if l == "\n":
                logger.debug("empty line")
                sys.stdout.write("\n")
                sys.stdout.flush()
    except BrokenPipeError:
        logger.debug("BrokenPipeError")
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)


if __name__ == "__main__":
    main()