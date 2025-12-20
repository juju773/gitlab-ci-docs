from pathlib import Path


def asciidoc_write(content: str, output: Path) -> None:
    output.write_text(content, encoding="utf-8")


class AsciiDocWriter:
    """
    Writes AsciiDoc content to disk.
    """

