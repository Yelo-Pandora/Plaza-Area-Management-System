import os
import argparse
from glob import glob

try:
    import cairosvg
except Exception as e:
    cairosvg = None


def convert_svg_to_png(svg_path, png_path, size=None):
    if cairosvg is None:
        raise RuntimeError('cairosvg is not installed. Run: pip install cairosvg')
    if size:
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)
    else:
        cairosvg.svg2png(url=svg_path, write_to=png_path)


def main():
    parser = argparse.ArgumentParser(description='Convert SVG icons to PNG')
    parser.add_argument('--input', '-i', required=True, help='Input directory containing svg files')
    parser.add_argument('--size', '-s', type=int, default=64, help='Output PNG size in px (square)')
    parser.add_argument('--delete', action='store_true', help='Delete original SVG files after conversion')
    args = parser.parse_args()

    svg_files = glob(os.path.join(args.input, '*.svg'))
    if not svg_files:
        print('No SVG files found in', args.input)
        return

    for svg in svg_files:
        name = os.path.splitext(os.path.basename(svg))[0]
        png = os.path.join(args.input, name + '.png')
        try:
            convert_svg_to_png(svg, png, size=args.size)
            print('Converted:', svg, '->', png)
        except Exception as e:
            print('Failed to convert', svg, ':', e)

    if args.delete:
        for svg in svg_files:
            try:
                os.remove(svg)
                print('Deleted:', svg)
            except Exception as e:
                print('Failed to delete', svg, ':', e)

if __name__ == '__main__':
    main()
