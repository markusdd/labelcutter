import pikepdf
import argparse
import pdf2image
from pathlib import Path

parser = argparse.ArgumentParser(
    prog='labelcutter',
    description='Handy CLI tool to extract the label portion from a larger PDF you got from your package carrier.',
    epilog='',
)

parser.add_argument("file")
parser.add_argument('-t', '--type', default="DHL_A4", choices=["DHL_A4"])
# parser.add_argument('-o', '--outfile', default="")
parser.add_argument('-f', '--format', default="", choices=["Brother_62mm"])

opts = parser.parse_args()

with pikepdf.open(opts.file) as pdf:

    page = pdf.pages[0]
    page.rotate(90, relative=True)
    c = page.mediabox
    filename = Path(opts.file).stem

    if not opts.format:

        # normal cropping for 103x199mm labels
        c[0] = 26  # upper margin
        c[1] = 490 # left margin
        c[2] = 583 # lower margin
        c[3] = 774 # right margin

        outname = f'{filename}_rotated_cropped_for103x199mm'
        pdf.save(f'{outname}.pdf')
        pages = pdf2image.convert_from_path(f'{outname}.pdf', dpi=203)
        for page in pages:
            page.save(f'{outname}.png', 'PNG')

    elif opts.format == "Brother_62mm":

        # slicing into 3 for 62mm endless Brother labels
        pdf_sliced = pikepdf.new()
        page_size = [280,170]
        rect = pikepdf.Rectangle(0,0,280,170)

        c[0] = 27  # upper margin
        c[1] = 490 # left margin
        c[2] = 210 # lower margin
        c[3] = 774 # right margin
        page_upper = pdf_sliced.add_blank_page(page_size=page_size)
        page_upper.add_overlay(page, rect, shrink=True, expand=True)

        c[0] = 211 # upper margin
        c[1] = 490 # left margin
        c[2] = 375 # lower margin
        c[3] = 774 # right margin
        page_middle = pdf_sliced.add_blank_page(page_size=page_size)
        page_middle.add_overlay(page, rect, shrink=True, expand=True)

        c[0] = 375 # upper margin
        c[1] = 490 # left margin
        c[2] = 583 # lower margin
        c[3] = 774 # right margin
        page_lower = pdf_sliced.add_blank_page(page_size=page_size)
        page_lower.add_overlay(page, rect, shrink=True, expand=True)

        outname = f'{filename}_rotated_cropped_sliced_forBrother62mm'
        names = ["upper", "middle", "lower"]
        pdf_sliced.save(f'{outname}.pdf')
        pages = pdf2image.convert_from_path(f'{outname}.pdf', dpi=300)
        for i, page in enumerate(pages):
            page.save(f'{outname}_{names[i]}.png', 'PNG')
    
