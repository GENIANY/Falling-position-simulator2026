#!/usr/bin/env python3
"""Build offline research readings from explicit source ranges; no network or Git mutation."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import urlsplit, urlunsplit


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inside(root: Path, name: str) -> Path:
    path = (root / name).resolve()
    if not path.is_relative_to(root) or Path(name).is_absolute():
        raise ValueError(f"source outside repository: {name}")
    return path


def rebase_links(text: str, source: str) -> str:
    """Make source-document links usable beside the generated packets."""
    def replace(match):
        target = match[2]
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or target.startswith('/'):
            return match[0]
        path = posixpath.normpath(posixpath.join(posixpath.dirname(source), parts.path)) if parts.path else source
        relative = posixpath.relpath(path, 'docs/research/packets')
        return match[1] + urlunsplit(('', '', relative, parts.query, parts.fragment)) + ')'
    return re.sub(r'(\[[^\]\n]*\]\()([^\s)]+)\)', replace, text)


class ReadableHTML(HTMLParser):
    """Keep headings, table cells, links and diagram alternatives in reading order."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style", "svg"}:
            if tag == "svg" and attrs.get("aria-label"):
                self.parts.append("\n[図の説明] " + attrs["aria-label"] + "\n")
            self.hidden += 1
        if self.hidden:
            return
        if tag in {"p", "div", "section", "tr", "ul", "ol", "figure", "details", "summary", "figcaption"}:
            self.parts.append("\n")
        if re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n" + "#" * int(tag[1]) + " ")
        if tag == "li":
            self.parts.append("\n- ")
        if tag in {"td", "th"}:
            self.parts.append(" | ")
        if tag == "br":
            self.parts.append("\n")
        if tag in {"sup", "sub"}:
            self.parts.append("^(" if tag == "sup" else "_(")
        if tag == "a":
            self.links.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg"}:
            self.hidden -= 1
            return
        if self.hidden:
            return
        if tag in {"sup", "sub"}:
            self.parts.append(")")
        if tag == "a" and self.links:
            href = self.links.pop()
            if href:
                self.parts.append(" (" + href + ")")
        if tag in {"p", "div", "section", "tr", "li", "summary", "figcaption"} or re.fullmatch(r"h[1-6]", tag):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", "".join(self.parts)).strip()


def extract(text: str, selection: dict) -> str:
    kind = selection.get("kind", "full")
    if kind == "full":
        return text
    if kind == "markdown":
        heading = selection["heading"]
        headings = []
        fence_char, fence_size, offset = None, 0, 0
        for line in text.splitlines(keepends=True):
            fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
            if fence_char:
                if fence and fence[1][0] == fence_char and len(fence[1]) >= fence_size and not fence[2].strip():
                    fence_char = None
            elif fence:
                fence_char, fence_size = fence[1][0], len(fence[1])
            else:
                title = line.rstrip()
                match = re.match(r"^(#{1,6}) ", title)
                if match:
                    headings.append((offset, len(match[1]), title))
            offset += len(line)
        matches = [i for i, (_, _, title) in enumerate(headings) if title == heading]
        if len(matches) != 1:
            raise ValueError(f"heading must occur once: {heading}")
        index = matches[0]
        start, level, _ = headings[index]
        end = next((offset for offset, depth, _ in headings[index + 1:] if depth <= level), len(text))
        return text[start:end]
    if kind == "html_id":
        # Use the same non-executing HTML span parser as the repository checker.
        from check_health import Spans
        bounds = Spans(text).spans.get(selection["id"])
        if bounds is None:
            raise ValueError(f"missing HTML id: {selection['id']}")
        return text[bounds[0]:bounds[1]]
    raise ValueError(f"unknown selection kind: {kind}")


def build(root: Path, spec: dict) -> dict[str, bytes]:
    outputs: dict[str, bytes] = {}
    manifests = {}
    for task, config in spec["tasks"].items():
        if not re.fullmatch(r"Q[0-9]{3}-[0-9]{2}", task):
            raise ValueError("invalid task id")
        pieces = [f"# {task} 調査用の読み物\n\n"
                  f"依頼版：{spec['version']}。基準main：`{spec['basis_commit']}`。\n"
                  "これは採用済みmainの比較基準で、下記抜粋は今回の候補本文です。未統合候補の比較元と、最終保存/統合SHAは区別してください。"
                  "SHAが不明でも本文を読めますが、最新mainを確認したとは扱いません。\n\n"
                  f"**今回の焦点は {task} です。共通入口の初回開始例は、別の課題へ切り替える指示ではありません。全体の目的を踏まえ、必要なら問いの分割や優先順にも異論を返してください。**\n\n"
                  "これは自動生成された課題別の読書束です。現在の正本は記載した元パス。"
                  "MarkdownのリンクはGit内の資料束の位置から辿れるように変換しています。単独添付では未同梱先へアクセスできると仮定せず、元パスから必要資料を求めてください。図の文字説明は含みますが、画面の操作確認や原図の視認を代替しません。\n"]
        sources = []
        for item in spec["common"] + config["sources"] + spec.get("closing", []):
            path = inside(root, item["path"])
            data = path.read_bytes()
            text = data.decode("utf-8")
            selected = extract(text, item)
            label = item.get("heading", item.get("id", "全文"))
            sources.append({"path": item["path"], "selection": label,
                            "source_sha256": sha(data), "excerpt_sha256": sha(selected.encode("utf-8"))})
            if path.suffix == ".html":
                parser = ReadableHTML()
                parser.feed(selected)
                parser.close()
                selected = parser.text()
            elif path.suffix in {".py", ".json"}:
                selected = "```" + ("python" if path.suffix == ".py" else "json") + "\n" + selected + "\n```"
            else:
                selected = rebase_links(selected, item['path'])
            pieces.append(f"\n---\n\n## 根拠：{item['path']} — {label}\n\n{selected.strip()}\n")
        if config.get("additional_reading"):
            pieces.append("\n## 必要になった場合に追加する原資料\n\n"
                          "次の資料はこの一冊に同梱したとみなさないでください。読めない場合は必要な箇所を要求します。\n\n"
                          + "\n".join("- " + item for item in config["additional_reading"]) + "\n")
        result = "\n".join(pieces).encode("utf-8")
        outputs[task + ".md"] = result
        manifests[task] = {"packet_sha256": sha(result), "bytes": len(result), "sources": sources,
                           "additional_reading": config.get("additional_reading", [])}
    manifest = {"schema": "research-packet/1", "version": spec["version"],
                "basis_commit": spec["basis_commit"], "snapshot_status": "candidate_content_not_merge_sha",
                "spec_sha256": sha(json.dumps(spec, ensure_ascii=False, sort_keys=True).encode("utf-8")),
                "tasks": manifests}
    outputs["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="New directory only; never replaces existing files")
    parser.add_argument("--check", action="store_true", help="Compare regenerated bytes to tracked packets without writing")
    args = parser.parse_args()
    if args.check == bool(args.output):
        parser.error("choose exactly one of --check or --output NEW_DIRECTORY")
    root = args.root.resolve(strict=True)
    try:
        spec = json.loads((root / "docs/research/packet_sources.json").read_text(encoding="utf-8"))
        if not re.fullmatch(r"[0-9a-f]{40}", spec["basis_commit"]):
            raise ValueError("basis_commit must be a fixed commit")
        products = build(root, spec)
        if args.check:
            folder = root / "docs/research/packets"
            mismatches = [name for name, data in products.items() if not (folder / name).is_file() or (folder / name).read_bytes() != data]
            extras = sorted(p.name for p in folder.iterdir() if p.name not in products) if folder.is_dir() else []
            if mismatches or extras:
                raise ValueError(f"stale/missing packets={mismatches}; unexpected files={extras}")
            print(f"Verified {len(products)} generated research files; no source was changed.")
        else:
            args.output.mkdir(parents=True, exist_ok=False)
            for name, data in products.items():
                (args.output / name).write_bytes(data)
            print(f"Built {len(products)} research files in {args.output}")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
