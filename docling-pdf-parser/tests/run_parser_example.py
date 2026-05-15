import asyncio
import sys
from pathlib import Path

# Ensure local package imports work when running the script directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.docling_parser import DoclingParserService

async def main():
    p = Path("sample_test.txt")
    p.write_text("Hello world from sample file.\nThis is a test.", encoding="utf-8")

    svc = DoclingParserService()
    parsed = await svc.parse_file(str(p))
    print("PARSED:", parsed)

if __name__ == "__main__":
    asyncio.run(main())
