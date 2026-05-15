import json
from pathlib import Path
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption
from docling.datamodel.base_models import InputFormat



class DoclingParserService:
    def __init__(self):
        # Lazily initialize heavy DocumentConverter to avoid import-time failures
        self.converter = None

    async def parse_file(self, file_path: str) -> dict:
        """Parse any supported file and return a dict with metadata and content.

        Falls back to plain-text reading for simple text-like extensions if
        the converter raises an error.
        """
        path = Path(file_path)
        result = {
            "source_path": str(file_path),
            "filename": path.name,
            "extension": path.suffix.lower(),
            "content": "",
            "format": None,
            "error": None,
        }

        try:
            if self.converter is None:
                try:

                    self.converter = DocumentConverter()
                except Exception as ie:
                    # If docling can't be imported/initialized, fall back for text-like files
                    if path.suffix.lower() in (".txt", ".md", ".csv"):
                        try:
                            text = path.read_text(encoding="utf-8", errors="ignore")
                            result.update({"content": text, "format": "text"})
                            return result
                        except Exception as e2:
                            result.update({"error": f"text-read-failed: {e2}"})
                            return result
                    result.update({"error": f"docling-import-failed: {ie}"})
                    return result

            doc = self.converter.convert(file_path).document
            content = doc.export_to_markdown()
            result.update({"content": content, "format": "docling"})
        except Exception as e:
            # Fallback for plain text-like files
            if path.suffix.lower() in (".txt", ".md", ".csv"):
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    result.update({"content": text, "format": "text"})
                except Exception as e2:
                    result.update({"error": f"text-read-failed: {e2}"})
            else:
                result.update({"error": str(e)})

        return result

    async def parse_pdf(self, file_path: str) -> str:
        # Backwards-compatible wrapper
        parsed = await self.parse_file(file_path)
        return parsed.get("content", "")

    async def parse_from_stream(self, name: str, data: bytes) -> dict:
        """Parse a binary stream (bytes) and return same dict shape as parse_file."""
        from io import BytesIO

        path_like = name or "stream"
        result = {
            "source_path": path_like,
            "filename": path_like,
            "extension": Path(name).suffix.lower() if name else "",
            "content": "",
            "format": None,
            "error": None,
        }

        try:
            if self.converter is None:
                try:
                    self.converter = DocumentConverter()
                except Exception as ie:
                        # Attempt to decode as UTF-8 text for common text-like streams
                        if name and Path(name).suffix.lower() in (".txt", ".md", ".csv"):
                            try:
                                text = data.decode("utf-8", errors="ignore")
                                result.update({"content": text, "format": "text"})
                                return result
                            except Exception as e2:
                                result.update({"error": f"stream-text-decode-failed: {e2}"})
                                return result
                        result.update({"error": f"docling-import-failed: {ie}"})
                        return result


            buf = BytesIO(data)
            stream = DocumentStream(name=name or "stream", stream=buf)
            res = self.converter.convert(stream)
            doc = res.document
            result.update({"content": doc.export_to_markdown(), "format": "docling"})
        except Exception as e:
            result.update({"error": str(e)})

        return result

    async def parse_batch(self, inputs: list, output_dir: str = None, export: str = "markdown") -> list:
        """Process a batch of inputs (paths or URLs). Returns list of dicts with status and saved path when possible."""
        results = []
        out_dir = Path(output_dir) if output_dir else Path("parsed")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Try lazy-importing converter; if it fails, we still attempt to handle plain-text inputs
        converter = None
        try:
            converter = DocumentConverter()
        except Exception:
            converter = None

        for inp in inputs:
            item = {"input": inp, "status": "failed", "error": None, "saved_to": None}
            try:
                if converter is not None:
                    # converter.convert_all may be available; use single convert for simplicity
                    res = converter.convert(inp)
                    if hasattr(res, "status"):
                        item["status"] = getattr(res, "status")
                    doc = res.document
                    if export == "markdown":
                        text = doc.export_to_markdown()
                        ext = ".md"
                    elif export == "text":
                        text = doc.export_to_text()
                        ext = ".txt"
                    elif export == "dict":
                        text = doc.export_to_dict()
                        ext = ".json"
                    elif export == "html":
                        text = doc.export_to_html()
                        ext = ".html"
                    else:
                        text = doc.export_to_markdown()
                        ext = ".md"

                    fname = Path(inp).stem if isinstance(inp, str) else "input"
                    out_path = out_dir / f"{fname}{ext}"
                    # write JSON for dict, else text
                    if ext == ".json":
                        out_path.write_text(json.dumps(text, ensure_ascii=False, indent=2), encoding="utf-8")
                    else:
                        out_path.write_text(str(text), encoding="utf-8")

                    item.update({"status": "success", "saved_to": str(out_path)})
                else:
                    # fallback: if it's a local text file, read and save
                    p = Path(inp)
                    if p.exists() and p.suffix.lower() in (".txt", ".md", ".csv"):
                        text = p.read_text(encoding="utf-8", errors="ignore")
                        out_path = out_dir / f"{p.stem}.txt"
                        out_path.write_text(text, encoding="utf-8")
                        item.update({"status": "success", "saved_to": str(out_path)})
                    else:
                        item.update({"error": "docling-unavailable-and-input-not-text"})
                results.append(item)
            except Exception as e:
                item.update({"error": str(e)})
                results.append(item)

        return results

    async def parse_from_url(self, url: str) -> str:
        # Lazy import and convert from a URL
        if self.converter is None:
            self.converter = DocumentConverter()

        doc = self.converter.convert(url).document
        return doc.export_to_markdown()

    async def pipeline_format(self, file_path: str, do_ocr: bool = False, do_table_structure: bool = False, generate_pic_image: bool = False) -> str:
        # Placeholder for future implementation of a more complex pipeline

        pipeline_options = PdfPipelineOptions(
            do_ocr=do_ocr,
            do_table_structure=do_table_structure,
            generate_picture_images=generate_pic_image,  # Extract images/figures
        )

        # 2. Set the image scale (e.g., 2.0 for double resolution)
        pipeline_options.images_scale = 2.0 

        # 3. Enable image generation (required to actually produce the images)
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        doc = converter.convert(file_path).document
        figures_dir = Path(f"extracted_figures/{Path(file_path).stem}")
        figures_dir.mkdir(exist_ok=True)
        # store images 
        for i, pic in enumerate(doc.pictures):
            if pic.image:
                pic.image.pil_image.save(figures_dir / f"fig_{i+1}.png")
                print(f"fig_{i+1}.png — caption: {pic.caption_text(doc)[:60]}")

        return doc.export_to_markdown()