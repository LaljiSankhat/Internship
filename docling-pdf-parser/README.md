# Docling PDF Parser - Enhanced

This project exposes a small FastAPI wrapper around Docling features and adds some helpful endpoints and utilities for testing.

Run locally (with reload):

```bash
uvicorn main:app --reload --port 8001
```

API endpoints

- `GET /` - welcome message
- `POST /upload?to=markdown|text|dict|html` - upload a file; `to` controls export type (markdown default)
- `POST /upload-stream` - upload file as stream (uses docling DocumentStream)
- `POST /batch` - JSON body `{"inputs": ["file1.pdf", "file2.docx"]}` to batch-convert
- `POST /from-url` - parse by URL
- `POST /pipeline-format` - PDF pipeline options: `do_ocr`, `do_table_structure`, `generate_pic_image`

Examples

Upload a text file and get markdown:

```bash
curl -F "file=@sample.txt" http://localhost:8001/upload
```

Batch parse local files (server must be running):

```bash
curl -X POST "http://localhost:8001/batch" -H "Content-Type: application/json" -d '{"inputs": ["sample.txt"]}'
```

Notes

- The service uses lazy imports for `docling` to avoid import-time failures in environments
  without all optional dependencies; plain text files will be handled as a fallback.
- Outputs are written to the `outputs/` directory with timestamp+UUID filenames.

Testing

Run example scripts:

```bash
python tests/run_parser_example.py
python tests/run_service_examples.py
```
