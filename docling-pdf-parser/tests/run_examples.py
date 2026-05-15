import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.docling_examples import (
    parse_any_file, parse_from_url, parse_from_stream, check_result_status,
    export_options_example, supported_formats, pdf_pipeline_example, batch_parse
)

async def main():
    p = Path('documents/cloudflare.png')
    p.write_text('Example content for docling_examples test.\nLine 2.', encoding='utf-8')

    print('\n--- parse_any_file')
    print(parse_any_file(str(p)))

    print('\n--- parse_from_stream')
    data = p.read_bytes()
    print(parse_from_stream(p.name, data))

    print('\n--- export_options_example')
    print(export_options_example(str(p)))

    print('\n--- supported_formats')
    print(supported_formats())

    print('\n--- batch_parse')
    print(batch_parse([str(p)], export='text', output_dir='parsed_examples'))

if __name__ == '__main__':
    asyncio.run(main())
