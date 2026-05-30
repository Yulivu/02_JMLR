"""Fetch CoNLL-2000 chunking files for the optional public BIO case.

The script records provenance but does not make the dataset a committed result.
Review licensing before tracking or redistributing downloaded files.
"""

from __future__ import annotations

import gzip
import hashlib
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve


FILES: dict[str, list[str]] = {
    "train.txt": [
        "https://www.clips.uantwerpen.be/conll2000/chunking/train.txt.gz",
        "http://www.cnts.ua.ac.be/conll2000/chunking/train.txt.gz",
        "https://raw.githubusercontent.com/teropa/nlp/master/resources/corpora/conll2000/train.txt",
    ],
    "test.txt": [
        "https://www.clips.uantwerpen.be/conll2000/chunking/test.txt.gz",
        "http://www.cnts.ua.ac.be/conll2000/chunking/test.txt.gz",
        "https://raw.githubusercontent.com/teropa/nlp/master/resources/corpora/conll2000/test.txt",
    ],
}

MD5_GZ = {
    "train.txt": "6969c2903a1f19a83569db643e43dcc8",
    "test.txt": "a916e1c2d83eb3004b38fc6fcd628939",
}

MD5_TXT = {
    "train.txt": "2e2f24e90e20fcb910ab2251b5ed8cd0",
    "test.txt": "56944df34be553b72a2a634e539a0951",
}


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_with_fallback(urls: list[str], path: Path) -> str:
    errors: list[str] = []
    for url in urls:
        try:
            print(f"FETCH {url} -> {path}")
            urlretrieve(url, path)
            return url
        except (HTTPError, URLError, OSError) as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("all CoNLL2000 download URLs failed:\n" + "\n".join(errors))


def fetch_file(filename: str, urls: list[str], output_dir: Path) -> str:
    out_path = output_dir / filename
    errors: list[str] = []
    for url in urls:
        try:
            if url.endswith(".gz"):
                gz_path = output_dir / f"{filename}.gz"
                resolved_url = fetch_with_fallback([url], gz_path)
                actual_gz_md5 = md5_file(gz_path)
                if actual_gz_md5 != MD5_GZ[filename]:
                    raise RuntimeError(
                        f"MD5 mismatch for {gz_path}: expected {MD5_GZ[filename]}, got {actual_gz_md5}"
                    )
                with gzip.open(gz_path, "rb") as source, out_path.open("wb") as target:
                    target.write(source.read())
            else:
                resolved_url = fetch_with_fallback([url], out_path)
            actual_txt_md5 = md5_file(out_path)
            if actual_txt_md5 != MD5_TXT[filename]:
                raise RuntimeError(
                    f"MD5 mismatch for {out_path}: expected {MD5_TXT[filename]}, got {actual_txt_md5}"
                )
            print(f"WROTE {out_path}")
            return resolved_url
        except (RuntimeError, OSError) as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError(f"all sources failed for {filename}:\n" + "\n".join(errors))


def main() -> None:
    output_dir = Path("data/raw/conll2000_chunking")
    output_dir.mkdir(parents=True, exist_ok=True)
    resolved_urls: dict[str, str] = {}
    for filename, urls in FILES.items():
        resolved_urls[filename] = fetch_file(filename, urls, output_dir)
    provenance = [
        "# CoNLL-2000 Chunking Local Provenance",
        "",
        "Downloaded by `scripts/data/fetch_conll2000_chunking.py`.",
        "The script attempts historical official CoNLL2000 URLs first and falls back to the GitHub mirror when those hosts are unavailable.",
        "",
        "| local file | source URL | MD5 text hash |",
        "|---|---|---|",
    ]
    for filename, url in resolved_urls.items():
        provenance.append(f"| `data/raw/conll2000_chunking/{filename}` | `{url}` | `{MD5_TXT[filename]}` |")
    provenance.extend(
        [
            "",
            "Use only as an optional public BIO/chunking case after reviewing redistribution and citation requirements.",
            "",
        ]
    )
    (output_dir / "PROVENANCE.md").write_text("\n".join(provenance), encoding="utf-8")


if __name__ == "__main__":
    main()
