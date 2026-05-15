"""Helper functions implementing Docling spec examples with safe lazy imports.

Each function mirrors an example in the spec and returns serializable results
or writes output files in the `outputs/` directory. The functions avoid hard
dependencies by falling back to simple behavior when `docling` is unavailable.
"""
from pathlib import Path
import json
from typing import List, Any, Dict



def _ensure_converter():
    try:
        from docling.document_converter import DocumentConverter

        return DocumentConverter()
    except Exception as e:
        raise RuntimeError(f"docling unavailable: {e}")


def parse_any_file(path: str) -> Dict[str, Any]:
    """One-liner parse that returns markdown, text, and dict when possible."""
    p = Path(path)
    try:
        conv = _ensure_converter()
        res = conv.convert(path)
        doc = res.document
        return {
            "export_markdown": doc.export_to_markdown(),
            "export_text": doc.export_to_text(),
            "export_dict": doc.export_to_dict(),
            "status": getattr(res, "status", "unknown"),
        }
    except RuntimeError as e:
        # Fallback for plain text
        if p.exists() and p.suffix.lower() in (".txt", ".md", ".csv"):
            return {"export_text": p.read_text(encoding="utf-8", errors="ignore"), "status": "fallback-text"}
        return {"error": str(e)}


def parse_from_url(url: str) -> Dict[str, Any]:
    try:
        conv = _ensure_converter()
        res = conv.convert(url)
        return {"markdown": res.document.export_to_markdown(), "status": getattr(res, "status", "unknown")}
    except Exception as e:
        return {"error": str(e)}


def parse_from_stream(name: str, data: bytes) -> Dict[str, Any]:
    try:
        conv = _ensure_converter()
        from io import BytesIO
        from docling.datamodel.base_models import DocumentStream

        buf = BytesIO(data)
        stream = DocumentStream(name=name, stream=buf)
        res = conv.convert(stream)
        return {"markdown": res.document.export_to_markdown(), "status": getattr(res, "status", "unknown")}
    except Exception as e:
        # Fallback to text decode
        try:
            s = data.decode("utf-8", errors="ignore")
            return {"text": s, "status": "fallback-text"}
        except Exception as e2:
            return {"error": str(e)}


def check_result_status(path: str) -> Dict[str, Any]:
    try:
        conv = _ensure_converter()
        from docling.datamodel.base_models import ConversionStatus

        res = conv.convert(path)
        status = getattr(res, "status", None)
        if status == ConversionStatus.SUCCESS:
            return {"status": "success", "markdown": res.document.export_to_markdown()}
        elif status == ConversionStatus.PARTIAL_SUCCESS:
            return {"status": "partial", "markdown": res.document.export_to_markdown(), "errors": getattr(res, "errors", None)}
        else:
            return {"status": "failed", "errors": getattr(res, "errors", None)}
    except Exception as e:
        return {"error": str(e)}


def export_options_example(path: str) -> Dict[str, Any]:
    try:
        conv = _ensure_converter()
        res = conv.convert(path)
        doc = res.document
        return {
            "markdown": doc.export_to_markdown(),
            "text": doc.export_to_text(),
            "html": doc.export_to_html(),
            "dict": doc.export_to_dict(),
        }
    except Exception as e:
        return {"error": str(e)}


def supported_formats() -> List[str]:
    # Mirror the spec list
    return [
        "pdf", "docx", "pptx", "xlsx", "html", "md", "adoc", "tex", "csv", "txt", "png", "jpg", "tiff", "xml"
    ]


def pdf_pipeline_example(path: str, do_ocr: bool = True, do_table_structure: bool = True, generate_picture_images: bool = False) -> Dict[str, Any]:
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        pipeline_options = PdfPipelineOptions(do_ocr=do_ocr, do_table_structure=do_table_structure, generate_picture_images=generate_picture_images)
        conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
        res = conv.convert(path)
        return {"status": getattr(res, "status", "unknown"), "markdown": res.document.export_to_markdown()}
    except Exception as e:
        return {"error": str(e)}


def batch_parse(inputs: List[str], export: str = "markdown", output_dir: str = "parsed_examples") -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(exist_ok=True)
    conv = None
    try:
        conv = _ensure_converter()
    except Exception:
        conv = None

    results = []
    for inp in inputs:
        try:
            if conv is not None:
                res = conv.convert(inp)
                doc = res.document
                if export == "markdown":
                    text = doc.export_to_markdown(); ext = ".md"
                elif export == "text":
                    text = doc.export_to_text(); ext = ".txt"
                elif export == "dict":
                    text = doc.export_to_dict(); ext = ".json"
                elif export == "html":
                    text = doc.export_to_html(); ext = ".html"
                else:
                    text = doc.export_to_markdown(); ext = ".md"

                fname = Path(inp).stem
                out_path = out / f"{fname}{ext}"
                if ext == ".json":
                    out_path.write_text(json.dumps(text, ensure_ascii=False, indent=2), encoding="utf-8")
                else:
                    out_path.write_text(str(text), encoding="utf-8")
                results.append({"input": inp, "saved_to": str(out_path)})
            else:
                p = Path(inp)
                if p.exists() and p.suffix.lower() in (".txt", ".md", ".csv"):
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    out_path = out / f"{p.stem}.txt"
                    out_path.write_text(text, encoding="utf-8")
                    results.append({"input": inp, "saved_to": str(out_path)})
                else:
                    results.append({"input": inp, "error": "docling-unavailable-and-input-not-text"})
        except Exception as e:
            results.append({"input": inp, "error": str(e)})

    return {"results": results}
