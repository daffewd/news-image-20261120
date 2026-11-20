"""make.fun entry: Sum up 20 November's world news in one image.

The front page (entry.png, 1024x1024) is pre-rendered and held in this
repository; this program copies it byte-for-byte to /output/entry.png.
No network, no randomness, no font or system dependency at run time, so
two runs always write identical bytes.
"""
import hashlib
import os
import shutil
import struct
import sys
import zlib

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


def _fail_image(path: str, reason: str) -> None:
    print(f"error: image {path}: {reason}", file=sys.stderr)
    sys.exit(1)


def _validate_png_structure(data: bytes, path: str) -> None:
    signature = b"\x89PNG\r\n\x1a\n"
    if len(data) < 8 or data[:8] != signature:
        _fail_image(path, "invalid PNG signature")
    offset = 8
    first_chunk = True
    seen_iend = False
    while offset < len(data):
        if offset + 8 > len(data):
            _fail_image(
                path,
                f"truncated PNG: incomplete chunk header at offset {offset}",
            )
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(data):
            _fail_image(
                path,
                f"truncated PNG: chunk {chunk_type!r} at offset {offset} "
                f"declares {length} data bytes but file ends early",
            )
        chunk_data = data[data_start:data_end]
        stored_crc = struct.unpack(">I", data[data_end:crc_end])[0]
        computed_crc = zlib.crc32(chunk_type)
        computed_crc = zlib.crc32(chunk_data, computed_crc) & 0xFFFFFFFF
        if computed_crc != stored_crc:
            _fail_image(
                path,
                f"corrupt PNG: CRC mismatch in chunk {chunk_type!r} "
                f"at offset {offset} (stored {stored_crc:#010x}, "
                f"computed {computed_crc:#010x})",
            )
        if first_chunk:
            if chunk_type != b"IHDR":
                _fail_image(
                    path,
                    f"invalid PNG: first chunk must be IHDR, "
                    f"got {chunk_type!r}",
                )
            if length != 13:
                _fail_image(
                    path,
                    f"invalid PNG: IHDR length must be 13, got {length}",
                )
            width, height = struct.unpack(">II", chunk_data[0:8])
            if not (1 <= width <= 1024) or not (1 <= height <= 1024):
                _fail_image(
                    path,
                    f"invalid PNG: IHDR dimensions {width}x{height} "
                    f"outside allowed range 1..1024",
                )
            first_chunk = False
        offset = crc_end
        if chunk_type == b"IEND":
            if length != 0:
                _fail_image(
                    path,
                    f"invalid PNG: IEND length must be 0, got {length}",
                )
            if offset != len(data):
                _fail_image(
                    path,
                    f"invalid PNG: {len(data) - offset} trailing "
                    f"byte(s) after IEND",
                )
            seen_iend = True
            break
    if first_chunk:
        _fail_image(path, "invalid PNG: missing IHDR chunk")
    if not seen_iend:
        _fail_image(path, "truncated PNG: missing complete IEND chunk")


def _validate_jpeg_structure(data: bytes, path: str) -> None:
    if len(data) < 4:
        _fail_image(
            path,
            f"truncated JPEG: {len(data)} bytes, too short for "
            f"SOI and EOI markers",
        )
    if data[0] != 0xFF or data[1] != 0xD8:
        _fail_image(
            path,
            f"invalid JPEG: missing SOI marker at start "
            f"(got {data[:2].hex()!r})",
        )
    if data[-2] != 0xFF or data[-1] != 0xD9:
        _fail_image(
            path,
            f"truncated JPEG: missing EOI marker at end "
            f"(got {data[-2:].hex()!r})",
        )


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
        _validate_png_structure(data, path)
        iend_trailer = b"\x00\x00\x00\x00IEND\xaeB`\x82"
        if not data.endswith(iend_trailer):
            print(
                f"error: image {path} is not a whole PNG: "
                f"missing IEND trailer (size {len(data)} bytes)",
                file=sys.stderr,
            )
            sys.exit(1)
        return
    if data.startswith(b"\xff\xd8"):
        _validate_jpeg_structure(data, path)
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
