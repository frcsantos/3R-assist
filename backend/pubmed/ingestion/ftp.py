"""Download PubMed baseline and update files from NCBI FTP."""

from __future__ import annotations

import ftplib
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

FTP_HOST = "ftp.ncbi.nlm.nih.gov"
BASELINE_DIR = "/pubmed/baseline"
UPDATEFILES_DIR = "/pubmed/updatefiles"


def list_baseline_files(ftp: ftplib.FTP) -> list[str]:
    ftp.cwd(BASELINE_DIR)
    return sorted(f for f in ftp.nlst() if f.endswith(".xml.gz"))


def list_update_files(ftp: ftplib.FTP) -> list[str]:
    ftp.cwd(UPDATEFILES_DIR)
    return sorted(f for f in ftp.nlst() if f.endswith(".xml.gz"))


def _verify_md5(path: Path, md5_path: Path) -> bool:
    # NCBI uses BSD format: "MD5 (filename) = <hash>"
    # GNU format is:        "<hash>  filename"
    # split()[-1] works for both.
    expected = md5_path.read_text().split()[-1].lower()
    actual = hashlib.md5(path.read_bytes()).hexdigest()
    return actual == expected


def download_file(
    ftp: ftplib.FTP,
    remote_name: str,
    dest_dir: Path,
    *,
    verify: bool = True,
) -> Path:
    dest = dest_dir / remote_name
    if dest.exists() and dest.stat().st_size > 0:
        logger.info("Already downloaded: %s", remote_name)
        return dest
    elif dest.exists():
        logger.warning("Removing empty/corrupt file: %s", remote_name)
        dest.unlink()

    logger.info("Downloading %s ...", remote_name)
    with dest.open("wb") as fh:
        ftp.retrbinary(f"RETR {BASELINE_DIR}/{remote_name}", fh.write)

    if verify:
        md5_remote = remote_name + ".md5"
        md5_local = dest_dir / md5_remote
        if not md5_local.exists():
            try:
                with md5_local.open("wb") as fh:
                    ftp.retrbinary(f"RETR {BASELINE_DIR}/{md5_remote}", fh.write)
            except Exception as exc:
                logger.warning("Could not fetch MD5 for %s (%s) — skipping verification", remote_name, exc)
                md5_local.unlink(missing_ok=True)
                return dest
        parts = md5_local.read_text().split()
        if not parts:
            logger.warning("Empty MD5 file for %s — skipping verification", remote_name)
            md5_local.unlink(missing_ok=True)
            return dest
        if not _verify_md5(dest, md5_local):
            dest.unlink(missing_ok=True)
            raise RuntimeError(f"MD5 mismatch for {remote_name}")

    return dest


def connect() -> ftplib.FTP:
    ftp = ftplib.FTP(FTP_HOST, timeout=120)
    ftp.login()
    return ftp
