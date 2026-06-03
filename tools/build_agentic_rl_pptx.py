#!/usr/bin/env python3
"""Build a simple PPTX deck from reports/agentic_rl_survey_cn_slides.md.

The script avoids external dependencies so it can run in restricted environments.
It creates a valid OpenXML PowerPoint file with title + bullet slides.
"""
from __future__ import annotations

import base64
import html
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reports" / "agentic_rl_survey_cn_slides.md"
OUT = ROOT / "reports" / "agentic_rl_survey_cn.pptx"
ROOT_OUT = ROOT / "agentic_rl_survey_cn.pptx"
REPORT_B64 = OUT.with_suffix(OUT.suffix + ".base64")
ROOT_B64 = ROOT_OUT.with_suffix(ROOT_OUT.suffix + ".base64")
ZIP_TIMESTAMP = (2026, 6, 3, 0, 0, 0)


def write_xml(z: zipfile.ZipFile, name: str, content: str) -> None:
    """Write a PPTX XML part with a stable timestamp for reproducible output."""
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, content)


def parse_slides(text: str):
    chunks = re.split(r"^## ", text, flags=re.M)
    slides = []
    for chunk in chunks[1:]:
        lines = chunk.strip().splitlines()
        if not lines:
            continue
        raw_title = lines[0].strip()
        title = raw_title.split("｜", 1)[-1].strip() if "｜" in raw_title else raw_title
        bullets = []
        in_body = False
        for line in lines[1:]:
            s = line.strip()
            if s == "**正文要点**":
                in_body = True
                continue
            if s.startswith("**") and s.endswith("**") and s != "**正文要点**":
                in_body = False
            if in_body and s.startswith("- "):
                bullets.append(s[2:].strip())
        slides.append((title, bullets))
    return slides


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def content_types(n: int) -> str:
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    overrides.extend(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, n + 1)
    )
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
%s
</Types>""" % "\n".join(overrides)


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def app_props(n: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>Codex</Application><PresentationFormat>Widescreen</PresentationFormat><Slides>{n}</Slides><Notes>0</Notes><HiddenSlides>0</HiddenSlides><Company>OpenAI</Company>
</Properties>"""


def core_props() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>Agentic RL 中文调研报告</dc:title><dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2026-06-03T00:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-06-03T00:00:00Z</dcterms:modified>
</cp:coreProperties>"""


def presentation(n: int) -> str:
    ids = "\n".join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, n + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{n+1}"/></p:sldMasterIdLst>
<p:sldIdLst>{ids}</p:sldIdLst>
<p:sldSz cx="12192000" cy="6858000" type="wide"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/>
</p:presentation>"""


def presentation_rels(n: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, n + 1)
    ]
    rels.append(f'<Relationship Id="rId{n+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>')
    return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">\n" + "\n".join(rels) + "\n</Relationships>"


def slide_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def text_run(text: str, size: int, bold: bool = False, color: str = "1F2937") -> str:
    b = " b=\"1\"" if bold else ""
    return f'<a:r><a:rPr lang="zh-CN" sz="{size}"{b}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="DengXian"/><a:ea typeface="DengXian"/></a:rPr><a:t>{esc(text)}</a:t></a:r>'


def paragraph(text: str, idx: int) -> str:
    # Wrap long bullets manually at visual phrase boundaries by leaving PowerPoint to wrap within box.
    prefix = "• "
    return f'<a:p><a:pPr marL="0" indent="0"><a:buNone/></a:pPr>{text_run(prefix + text, 2100, False)}</a:p>'


def slide_xml(title: str, bullets: list[str], num: int) -> str:
    # Include at most 6 bullets on slide; markdown has the detailed version.
    shown = bullets[:6]
    body = "\n".join(paragraph(b, i) for i, b in enumerate(shown))
    subtitle = "Agentic Reinforcement Learning｜中文调研草稿"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill></p:bgPr></p:bg><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="520000" y="360000"/><a:ext cx="11100000" cy="720000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr wrap="square"/><a:lstStyle/><a:p>{text_run(title, 3100, True, "0F172A")}</a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="760000" y="1350000"/><a:ext cx="10650000" cy="4400000"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:ln><a:srgbClr val="E2E8F0"/></a:ln></p:spPr><p:txBody><a:bodyPr lIns="220000" tIns="180000" rIns="220000" bIns="180000" wrap="square"/><a:lstStyle/>{body}</p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="4" name="Footer"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="520000" y="6250000"/><a:ext cx="11100000" cy="260000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p>{text_run(subtitle + f"  ·  {num:02d}", 1200, False, "64748B")}</a:p></p:txBody></p:sp>
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"""


def slide_master() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>"""


def master_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>"""


def layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"""


def layout_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>"""


def theme_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="AgenticRL"><a:themeElements><a:clrScheme name="AgenticRL"><a:dk1><a:srgbClr val="0F172A"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="334155"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2><a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="7C3AED"/></a:accent2><a:accent3><a:srgbClr val="059669"/></a:accent3><a:accent4><a:srgbClr val="F97316"/></a:accent4><a:accent5><a:srgbClr val="DC2626"/></a:accent5><a:accent6><a:srgbClr val="0891B2"/></a:accent6><a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink></a:clrScheme><a:fontScheme name="DengXian"><a:majorFont><a:latin typeface="DengXian"/><a:ea typeface="DengXian"/><a:cs typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="DengXian"/><a:ea typeface="DengXian"/><a:cs typeface="Arial"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>"""


def main() -> None:
    slides = parse_slides(SRC.read_text(encoding="utf-8"))
    if not slides:
        raise SystemExit("No slides parsed")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        n = len(slides)
        write_xml(z, "[Content_Types].xml", content_types(n))
        write_xml(z, "_rels/.rels", root_rels())
        write_xml(z, "docProps/app.xml", app_props(n))
        write_xml(z, "docProps/core.xml", core_props())
        write_xml(z, "ppt/presentation.xml", presentation(n))
        write_xml(z, "ppt/_rels/presentation.xml.rels", presentation_rels(n))
        write_xml(z, "ppt/slideMasters/slideMaster1.xml", slide_master())
        write_xml(z, "ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels())
        write_xml(z, "ppt/slideLayouts/slideLayout1.xml", layout_xml())
        write_xml(z, "ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels())
        write_xml(z, "ppt/theme/theme1.xml", theme_xml())
        for i, (title, bullets) in enumerate(slides, start=1):
            write_xml(z, f"ppt/slides/slide{i}.xml", slide_xml(title, bullets, i))
            write_xml(z, f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels())
    shutil.copyfile(OUT, ROOT_OUT)
    encoded = base64.b64encode(OUT.read_bytes()).decode("ascii")
    wrapped = "\n".join(encoded[i : i + 76] for i in range(0, len(encoded), 76)) + "\n"
    REPORT_B64.write_text(wrapped, encoding="ascii")
    ROOT_B64.write_text(wrapped, encoding="ascii")
    print(f"Wrote {OUT}, {ROOT_OUT}, {REPORT_B64}, and {ROOT_B64} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
