"""make.fun entry: Sum up 20 November's world news in one image.

The front page (entry.png, 1024x1024) is pre-rendered and held in this
repository; this program copies it byte-for-byte to /output/entry.png.
No network, no randomness, no font or system dependency at run time, so
two runs always write identical bytes.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_image(path: str) -> None:
    size = os.path.getsize(path)
    if size > 1048576:
        print(
            f"error: image {path} is {size} bytes, "
            f"exceeds 1 MiB limit (1048576 bytes)",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(path, "rb") as fh:
        data = fh.read()
    png_signature = b"\x89PNG\r\n\x1a\n"
    if data.startswith(png_signature):
        if len(data) < 24:
            print(
                f"error: image {path} is a truncated PNG: "
                f"{len(data)} bytes, too short for IHDR",
                file=sys.stderr,
            )
            sys.exit(1)
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        if width > 1024 or height > 1024:
            print(
                f"error: image {path} is {width}x{height}, "
                f"exceeds 1024x1024 limit",
                file=sys.stderr,
            )
            sys.exit(1)
        iend_trailer = b"\x00\x00\x00\x00IEND\xaeB`\x82"
        if not data.endswith(iend_trailer):
            print(
                f"error: image {path} is not a whole PNG: "
                f"missing IEND trailer (size {len(data)} bytes)",
                file=sys.stderr,
            )
            sys.exit(1)
        return
    if data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"):
        return
    print(
        f"error: image {path} is neither a whole PNG nor JPEG: "
        f"starts with {data[:8].hex() if data else ''!r} "
        f"and ends with {data[-2:].hex() if len(data) >= 2 else ''!r} "
        f"(size {size} bytes)",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    _validate_image(SRC)
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    src_digest = _sha256(SRC)
    dst_digest = _sha256(DST)
    if src_digest != dst_digest:
        os.remove(DST)
        print(
            f"error: verification failed for {DST}: "
            f"sha256 {dst_digest} != source {src_digest}",
            file=sys.stderr,
        )
        sys.exit(1)
    size = os.path.getsize(DST)
    print(f"wrote {DST} ({size} bytes) sha256={dst_digest}")


if __name__ == "__main__":
    sys.exit(main())
