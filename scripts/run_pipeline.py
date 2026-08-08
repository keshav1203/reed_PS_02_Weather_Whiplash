#!/usr/bin/env python3
"""CLI entry point for the Weather Whiplash data pipeline."""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path so we can import src.pipeline
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import PipelineConfig, WeatherWhiplashPipeline

def main():
    parser = argparse.ArgumentParser(
        description='Weather Whiplash Data Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--input', '-i', required=True, help='Input file or directory')
    parser.add_argument('--sampling-fps', type=float, default=None, help='Video sampling FPS (default: 2.0)')
    parser.add_argument('--width', type=int, default=None, help='Model input width (default: 640)')
    parser.add_argument('--height', type=int, default=None, help='Model input height (default: 640)')
    parser.add_argument('--base-dir', type=str, default=None, help='Base output directory (default: data)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    
    # Build config with overrides
    config_kwargs = {}
    if args.sampling_fps is not None:
        config_kwargs['sampling_fps'] = args.sampling_fps
    if args.width is not None:
        config_kwargs['model_width'] = args.width
    if args.height is not None:
        config_kwargs['model_height'] = args.height
    if args.base_dir is not None:
        config_kwargs['base_dir'] = Path(args.base_dir)
    
    config = PipelineConfig(**config_kwargs)
    
    # Print banner
    print('\n' + '=' * 40)
    print('  Weather Whiplash Data Pipeline')
    print('=' * 40 + '\n')
    
    # Run pipeline
    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Error: Input path does not exist: {input_path}')
        sys.exit(1)
    
    pipeline = WeatherWhiplashPipeline(config)
    result = pipeline.run(input_path)
    
    # Print summary
    print('\n' + '=' * 40)
    print('  Pipeline Summary')
    print('=' * 40)
    print(f'\n  Files discovered:     {result.files_discovered}')
    print(f'  Images:               {result.images_found}')
    print(f'  Videos:               {result.videos_found}')
    print(f'')
    print(f'  Processed:            {result.processed}')
    print(f'  Rejected:             {result.rejected}')
    print(f'  Duplicates:           {result.duplicates}')
    print(f'')
    print(f'  Images generated:     {result.images_generated}')
    print(f'  Video frames generated: {result.frames_generated}')
    print(f'')
    
    if result.errors:
        print(f'  Errors: {len(result.errors)}')
        for err in result.errors:
            print(f'    - {err}')
        print()
    
    if result.rejected == 0 and not result.errors:
        print('  Pipeline completed successfully.\n')
    else:
        print('  Pipeline completed with issues.\n')
    
    print('=' * 40 + '\n')

if __name__ == '__main__':
    main()
