from fastapi import FastAPI, File, UploadFile
import uvicorn
import os
from pathlib import Path
import json
from datetime import datetime
from uuid import uuid4
import tempfile 

from services.docling_parser import DoclingParserService


app = FastAPI()
OUTPUT_DIR = Path("outputs")


@app.get("/")
async def root():
    return {"message": "Welcome to the file parser API. Use the /upload-pdf/ endpoint to upload a file."}

docling_service = DoclingParserService()


def _unique_output_path(base_name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = uuid4().hex
    base = Path(base_name).stem if base_name else "upload"
    output_file_name = f"{base}_{stamp}_{uid}.json"
    return OUTPUT_DIR / output_file_name


def save_output(path_or_name: str, payload: dict) -> Path:
    out_path = _unique_output_path(path_or_name)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


async def upload_document(file: UploadFile) -> Path:
    file_suffix = Path(file.filename).suffix if file.filename else ""
    data = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
        temp_file.write(data)
        return Path(temp_file.name)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    temp_file_path = await upload_document(file)

    try:
        start_time = datetime.utcnow()
        parsed = await docling_service.parse_file(temp_file_path)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        payload = {
            "filename": file.filename,
            "content": parsed.get("content"),
            "format": parsed.get("format"),
            "error": parsed.get("error"),
            "processing_time_seconds": duration
        }
        output_file_path = save_output(file.filename or "upload", payload)

        return {
            "filename": file.filename,
            "content": parsed.get("content"),
            "format": parsed.get("format"),
            "error": parsed.get("error"),
            "processing_time_seconds": duration,
            "saved_to": str(output_file_path)
        }
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)


@app.post("/upload-stream")
async def upload_stream(file: UploadFile = File(...)):
    data = await file.read()
    parsed = await docling_service.parse_from_stream(file.filename, data)
    payload = {
        "filename": file.filename,
        "parsed_format": parsed.get("format"),
        "error": parsed.get("error"),
        "content": parsed.get("content"),
    }
    output_file_path = save_output(file.filename or "stream", payload)
    return {"filename": file.filename, "saved_to": str(output_file_path), "parsed_format": parsed.get("format"), "error": parsed.get("error")}


@app.post("/batch")
async def batch_parse(inputs: list, export: str = "markdown"):
    results = await docling_service.parse_batch(inputs, output_dir=str(OUTPUT_DIR), export=export)
    output_file_path = save_output("batch", {"results": results})
    return {"saved_to": str(output_file_path), "results": results}

@app.post("/from-url")
async def parse_pdf_from_url(url: str):
    # parse_from_url returns a string result
    result = await docling_service.parse_from_url(url)
    payload = {"url": url, "content": result}
    output_file_path = save_output(url, payload)

    return {"url": url, "content": result, "saved_to": str(output_file_path)}

@app.post("/pipeline-format")
async def parse_pdf_pipeline_format(
    file: UploadFile = File(...), 
    do_ocr: bool = False, 
    do_table_structure: bool = False, 
    generate_pic_image: bool = False
):
    temp_file_path = await upload_document(file)
    start_time = datetime.utcnow()
    result = await docling_service.pipeline_format(temp_file_path, do_ocr, do_table_structure, generate_pic_image)
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    # payload = {"filename": file.filename, "content": result}

    payload = {
        "filename": file.filename, 
        "content": result, 
        "options": {
            "do_ocr": do_ocr,
            "do_table_structure": do_table_structure,
            "generate_pic_image": generate_pic_image
        }, 
        "processing_time_seconds": duration
    }
    output_file_path = save_output(file.filename or "pipeline", payload)

    # res = save_output(file.filename or "pipeline", payload)

    return {
        "filename": file.filename, 
        "content": result, 
        "saved_to": str(output_file_path),
        "options": {
            "do_ocr": do_ocr,
            "do_table_structure": do_table_structure,
            "generate_pic_image": generate_pic_image
        }, 
        "processing_time_seconds": duration,
        "output_file": str(output_file_path)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003)