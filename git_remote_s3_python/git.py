import subprocess
import sys

class GitError(Exception):
    pass

def bundle(*, folder: str, sha: str, ref: str):
    """Bundles the content of the folder into a sha.bundle file

    Args:
        folder (str): the folder to bundle
        sha (str): the sha of the bundle. A bundle is stored as sha.bundle
        ref (str): the ref to bundle
    """
 
    subprocess.run(
        ["git", "bundle", "create", f"{folder}/{sha}.bundle", ref],
        stdout=subprocess.PIPE,
        check=True,
    )

def unbundle(*, folder: str, sha: str, ref: str):
    """Unbundles the content of the bundle referred by the sha

    Args:
        folder (str): the folder where the bundle is located
        sha (str): the sha of the bundle. A bundle is stored as sha.bundle
        ref (str): the ref to checkout after unbundling
    """
    subprocess.run(
        ["git", "bundle", "unbundle", f"{folder}/{sha}.bundle", ref],
        stdout=sys.stderr,
        check=True,
    )

def rev_parse(ref: str) -> str:
    """Gets the sha of a ref

    Args:
        ref (str): the ref to get the sha for

    Raises:
        Exception: if the ref is not found

    Returns:
        str: _description_
    """
    
    result = subprocess.run(["git", "rev-parse", ref], stdout=subprocess.PIPE)
    if result.returncode != 0:
        raise GitError(f"fatal: {ref} not found")
    sha = result.stdout.decode("utf8").strip()
    return sha

