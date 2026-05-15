import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.docling_parser import DoclingParserService

async def main():
    svc = DoclingParserService()
    # sample text file
    p = Path("sample_test.txt")
    p.write_text("Sample content for batch and stream test.", encoding="utf-8")

    # test parse_file
    parsed = await svc.parse_file(str(p))
    print('parse_file:', parsed['format'], parsed['content'][:40])

    # test parse_from_stream
    data = p.read_bytes()
    parsed_stream = await svc.parse_from_stream(p.name, data)
    print('parse_from_stream:', parsed_stream.get('format'), parsed_stream.get('content')[:40])

    # test parse_batch
    batch = await svc.parse_batch([str(p)], output_dir='parsed_test', export='text')
    print('parse_batch:', batch)

if __name__ == '__main__':
    asyncio.run(main())
