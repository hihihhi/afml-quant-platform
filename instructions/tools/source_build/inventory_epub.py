#!/usr/bin/env python3
"""Inventory a user-supplied EPUB without discarding its original representations.

The extracted XHTML and original archive are the fidelity authority. Human-facing
summaries are never used to reconstruct source text. Commented MathML is recorded
separately from the rendered equation images: agreement is a review task, not an
assumption. No OCR, network access, or execution of source code is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import shutil
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from lxml import etree

XHTML = "http://www.w3.org/1999/xhtml"
EPUB = "http://www.idpf.org/2007/ops"
OPF = "http://www.idpf.org/2007/opf"
NS = {"h": XHTML, "opf": OPF, "epub": EPUB}
NUMBERED = re.compile(r"^(\d+(?:\.(?:\d+|A))+)(?:\s+)(.*)$")
HEADING_TAGS = {f"h{level}" for level in range(1, 7)}
MAX_EXPANDED_BYTES = 512 * 1024 * 1024


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_name(node: etree._Element) -> str:
    return etree.QName(node).localname if isinstance(node.tag, str) else "#comment"


def normalized(text: str) -> str:
    return " ".join(text.split())


def visible_text(node: etree._Element) -> str:
    """Read rendered text in order, excluding XML comments and their MathML."""
    pieces: list[str] = []

    def visit(element: etree._Element) -> None:
        if not isinstance(element.tag, str):
            return
        if element.text:
            pieces.append(element.text)
        for child in element:
            if local_name(child) == "br":
                pieces.append("\n")
            else:
                visit(child)
            if child.tail:
                pieces.append(child.tail)

    visit(node)
    return "".join(pieces)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_member(document: str, href: str) -> str | None:
    url = urlsplit(href)
    if url.scheme or url.netloc:
        return None
    target = unquote(url.path)
    if not target:
        return document
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(document), target))
    if resolved.startswith("../") or resolved.startswith("/"):
        raise ValueError(f"Unsafe source reference: {document}: {href}")
    return resolved


def extract_source(epub_path: Path, root: Path) -> dict[str, Any]:
    output = root / "instructions" / "01-source"
    private = output / "private"
    unpacked = private / "epub"
    unpacked.mkdir(parents=True, exist_ok=True)
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_comments=False)
    member_manifest: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []
    headings: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    math_comments: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    snippets: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    missing_references: list[dict[str, Any]] = []
    section_text: dict[str, str] = {}
    last_page: str | None = None

    with ZipFile(epub_path) as archive:
        entries = archive.infolist()
        names = {entry.filename for entry in entries}
        if len(names) != len(entries):
            raise ValueError("Duplicate archive paths are not accepted.")
        if sum(entry.file_size for entry in entries) > MAX_EXPANDED_BYTES:
            raise ValueError("Archive exceeds extraction safety limit.")
        for entry in entries:
            member = PurePosixPath(entry.filename)
            if member.is_absolute() or ".." in member.parts or "\\" in entry.filename:
                raise ValueError(f"Unsafe archive path: {entry.filename}")
            if ((entry.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError(f"Archive symlink is not accepted: {entry.filename}")
            if entry.is_dir():
                continue
            data = archive.read(entry)
            destination = unpacked.joinpath(*member.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            member_manifest.append({"path": entry.filename, "bytes": len(data), "sha256": sha256(data)})

        container = etree.fromstring(archive.read("META-INF/container.xml"), parser)
        package_path = container.xpath('//*[local-name()="rootfile"]')[0].get("full-path")
        if not package_path:
            raise ValueError("EPUB package path is absent.")
        package = etree.fromstring(archive.read(package_path), parser)
        items = {node.get("id"): node for node in package.findall("opf:manifest/opf:item", NS)}
        spine = []
        for reference in package.findall("opf:spine/opf:itemref", NS):
            item = items[reference.get("idref")]
            href = item.get("href")
            if not href:
                raise ValueError("Spine item has no href.")
            spine.append({"path": resolve_member(package_path, href), "linear": reference.get("linear", "yes")})
        metadata = {local_name(node): normalized(visible_text(node)) for node in package.find("opf:metadata", NS) if local_name(node) != "meta"}

        for spine_index, spine_item in enumerate(spine):
            member = spine_item["path"]
            if member is None:
                raise ValueError("External spine documents are not supported.")
            tree = etree.fromstring(archive.read(member), parser)
            body = tree.find("h:body", NS)
            if body is None:
                raise ValueError(f"Missing body: {member}")
            doc_id = Path(member).stem
            chapter_match = re.fullmatch(r"c(\d+)", doc_id)
            chapter = int(chapter_match.group(1)) if chapter_match else None
            elements = list(body.iter())
            positions = {element: index for index, element in enumerate(elements)}
            node_pages: dict[etree._Element, str | None] = {}
            doc_headings: list[dict[str, Any]] = []
            doc_sections: list[dict[str, Any]] = []
            element_ids = {element.get("id") for element in elements if isinstance(element.tag, str) and element.get("id")}
            for index, element in enumerate(elements):
                if not isinstance(element.tag, str):
                    node_pages[element] = last_page
                    continue
                if element.get(f"{{{EPUB}}}type") == "pagebreak":
                    last_page = element.get("title") or element.get("id")
                    pages.append({"id": f"PAGE-{last_page}", "label": last_page, "document": member,
                                  "anchor": element.get("id"), "position": index, "spine_index": spine_index})
                node_pages[element] = last_page
                tag = local_name(element)
                if tag not in HEADING_TAGS:
                    continue
                text = normalized(visible_text(element))
                heading_id = f"H-{doc_id}-{len(doc_headings) + 1:03d}"
                number_match = NUMBERED.match(text)
                descendant_anchors = element.xpath('.//*[@id]/@id')
                local_page = next((child.get("title") for child in element.iter() if isinstance(child.tag, str) and child.get(f"{{{EPUB}}}type") == "pagebreak"), last_page)
                record = {"id": heading_id, "document": member, "chapter": chapter, "tag": tag,
                          "position": index, "title": text, "page": local_page,
                          "anchor": descendant_anchors[-1] if descendant_anchors else element.getparent().get("id"),
                          "xpath": element.getroottree().getpath(element),
                          "source_sha256": sha256(etree.tostring(element, with_tail=False))}
                if re.match(r"^SNIPPET\s+\d", text, re.IGNORECASE):
                    record["kind"] = "snippet"
                elif number_match and chapter:
                    record.update({"kind": "numbered_section", "number": number_match.group(1), "id": f"S-{number_match.group(1)}"})
                elif tag == "h1" and chapter:
                    record.update({"kind": "chapter", "number": str(chapter), "id": f"CH-{chapter:02d}"})
                else:
                    record["kind"] = "unnumbered"
                doc_headings.append(record)
                if chapter and record["kind"] != "snippet":
                    section = dict(record)
                    if record["kind"] == "unnumbered":
                        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
                        section["id"] = f"CH-{chapter:02d}-{slug}"
                    doc_sections.append(section)

            for i, section in enumerate(doc_sections):
                start = section["position"]
                end = doc_sections[i + 1]["position"] if i + 1 < len(doc_sections) else len(elements)
                section["position_end_exclusive"] = end
                section["page_end"] = next((node_pages[e] for e in reversed(elements[start:end]) if node_pages[e]), section["page"])
                number = section.get("number")
                if section["kind"] == "chapter":
                    section["parent"] = None
                elif section["kind"] == "numbered_section" and number and number.count(".") > 1:
                    parent_number = number.rsplit(".", 1)[0]
                    section["parent"] = f"S-{parent_number}" if any(s.get("number") == parent_number for s in doc_sections) else f"CH-{chapter:02d}"
                else:
                    section["parent"] = f"CH-{chapter:02d}"
                section["review_status"] = "extracted_not_semantically_approved"
                section["block_ids"] = []
                section["image_ids"] = []
                section["math_comment_ids"] = []
                section["table_ids"] = []
                section["snippet_ids"] = []

            def owner_for(index: int) -> dict[str, Any] | None:
                return next((s for s in reversed(doc_sections) if s["position"] <= index), None)

            for index, element in enumerate(elements):
                owner = owner_for(index)
                common = {"document": member, "position": index, "page": node_pages[element],
                          "section_id": owner["id"] if owner else None}
                tag = local_name(element)
                if tag == "#comment":
                    raw = element.text or ""
                    if "<math" in raw:
                        for offset, match in enumerate(re.finditer(r"<math\b.*?</math>", raw, flags=re.DOTALL)):
                            math_xml = match.group(0)
                            location = re.search(r'\blocation="([^"]+)"', math_xml)
                            record = {**common, "id": f"M-{doc_id}-{index:05d}-{offset}",
                                      "mathml": math_xml, "sha256": sha256(math_xml.encode()),
                                      "rendered_asset_basename": posixpath.basename(location.group(1)) if location else None,
                                      "representation": "commented_mathml_not_visible_source",
                                      "visual_agreement": "unreviewed"}
                            math_comments.append(record)
                            if owner:
                                owner["math_comment_ids"].append(record["id"])
                    continue
                if tag == "img":
                    src = element.get("src", "")
                    resolved = resolve_member(member, src)
                    exists = resolved in names
                    record = {**common, "id": f"IMG-{doc_id}-{index:05d}", "src": src, "asset": resolved,
                              "alt": element.get("alt"), "exists": exists,
                              "sha256": sha256(archive.read(resolved)) if exists else None,
                              "representation": "rendered_source_image"}
                    base = posixpath.basename(src)
                    record["kind"] = "inline_equation" if "_ILM" in base else "display_equation" if "_M" in base else "code_image" if re.match(r"s\d+-", base) else "figure_or_other"
                    images.append(record)
                    if owner:
                        owner["image_ids"].append(record["id"])
                    if not exists:
                        missing_references.append(record)
                if tag in HEADING_TAGS and re.match(r"^SNIPPET\s+\d", normalized(visible_text(element)), re.IGNORECASE):
                    parent = element.getparent()
                    record = {**common, "id": f"SNIP-{doc_id}-{len([s for s in snippets if s['document'] == member]) + 1:03d}",
                              "title": normalized(visible_text(element)),
                              "image_assets": [resolve_member(member, image.get("src", "")) for image in parent.findall(".//h:img", NS)],
                              "transcription_status": "source_image_preserved_transcription_pending"}
                    snippets.append(record)
                    if owner:
                        owner["snippet_ids"].append(record["id"])
                if tag == "table":
                    record = {**common, "id": f"TABLE-{doc_id}-{index:05d}", "rows": len(element.findall(".//h:tr", NS)),
                              "html": etree.tostring(element, encoding="unicode", with_tail=False)}
                    tables.append(record)
                    if owner:
                        owner["table_ids"].append(record["id"])
                if tag in {"p", "pre", "li", "td"} | HEADING_TAGS:
                    # Nested container text is intentionally recorded as such;
                    # source coverage validation does not sum these overlapping strings.
                    record = {**common, "id": f"B-{doc_id}-{index:05d}", "tag": tag,
                              "text": visible_text(element),
                              "xpath": element.getroottree().getpath(element),
                              "sha256": sha256(etree.tostring(element, with_tail=False))}
                    blocks.append(record)
                    if owner:
                        owner["block_ids"].append(record["id"])

            for section in doc_sections:
                owned = [b for b in blocks if b["section_id"] == section["id"] and b["tag"] in {"p", "pre"} | HEADING_TAGS]
                text = "\n\n".join(b["text"] for b in owned)
                section_text[section["id"]] = text
            private_text = private / "text" / f"{doc_id}.txt"
            private_text.parent.mkdir(parents=True, exist_ok=True)
            # Preserve individual visible-text character sequences. Whitespace is
            # normalized only for the independent comparison, not in this file.
            text = visible_text(body)
            private_text.write_text(text, encoding="utf-8")
            documents.append({**spine_item, "id": doc_id, "spine_index": spine_index, "chapter": chapter,
                              "body_text_sha256_normalized": sha256(normalized(text).encode()),
                              "visible_text_characters": len(text), "element_count": len(elements),
                              "image_count": len(body.findall(".//h:img", NS)), "anchors": sorted(element_ids)})
            headings.extend(doc_headings)
            sections.extend(doc_sections)

        nav_items = []
        for item in items.values():
            if "nav" not in item.get("properties", "").split():
                continue
            nav_path = resolve_member(package_path, item.get("href", ""))
            nav_tree = etree.fromstring(archive.read(nav_path), parser)
            for link in nav_tree.findall(".//h:a", NS):
                href = link.get("href", "")
                nav_items.append({"text": normalized(visible_text(link)), "href": href,
                                  "document": resolve_member(nav_path, href), "anchor": urlsplit(href).fragment})

    if not epub_path.resolve() == (private / "original.epub").resolve():
        shutil.copyfile(epub_path, private / "original.epub")
    basename_assets = {posixpath.basename(entry["asset"]): entry["asset"] for entry in images if entry["asset"]}
    for formula in math_comments:
        formula["rendered_asset"] = basename_assets.get(formula["rendered_asset_basename"])
    manifest = {"schema_version": 1, "source_filename": epub_path.name,
                "source_sha256": sha256(epub_path.read_bytes()), "metadata": metadata,
                "package_path": package_path, "archive_file_count": len(member_manifest),
                "spine_document_count": len(documents), "chapter_count": sum(d["chapter"] is not None for d in documents),
                "heading_count": len(headings), "section_node_count": len(sections),
                "numbered_section_count": sum(s["kind"] == "numbered_section" for s in sections),
                "page_marker_count": len(pages), "image_occurrence_count": len(images),
                "unique_rendered_assets": len({i["asset"] for i in images}),
                "image_kinds": dict(Counter(i["kind"] for i in images)),
                "commented_mathml_count": len(math_comments), "table_count": len(tables),
                "snippet_heading_count": len(snippets), "source_block_count": len(blocks),
                "missing_image_references": len(missing_references),
                "formatting_authority": "private/original.epub and private/epub (byte-exact)",
                "mathematical_verification": "not_complete", "rendered_image_transcription": "not_complete"}
    for name, value in [("manifest", manifest), ("archive_members", member_manifest), ("spine", documents),
                        ("headings", headings), ("sections", sections), ("pages", pages), ("images", images),
                        ("formulas", math_comments), ("tables", tables), ("snippets", snippets), ("navigation", nav_items)]:
        write_json(output / f"{name}.json", value)
    write_json(private / "section_text.json", section_text)
    with (private / "blocks.jsonl").open("w", encoding="utf-8") as stream:
        for block in blocks:
            stream.write(json.dumps(block, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest

# CLI entry point: instructions/tools/rebuild_private_source.py.
