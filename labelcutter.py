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
parser.add_argument('-t', '--type', default="DHL_A4", choices=["DHL_A4", "Hermes_A4"])
# parser.add_argument('-o', '--outfile', default="")
parser.add_argument('-f', '--format', default="", choices=["Brother_62mm"])

opts = parser.parse_args()

with pikepdf.open(opts.file) as pdf:

    page = pdf.pages[0]
    filename = Path(opts.file).stem

    match opts.type:
        case "DHL_A4":
            page.rotate(90, relative=True)
            c = page.mediabox
            if opts.format == "Brother_62mm":
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
            else: 
                # normal cropping for 103x199mm DHL labels
                c[0] = 26  # upper margin
                c[1] = 490 # left margin
                c[2] = 583 # lower margin
                c[3] = 774 # right margin

                outname = f'{filename}_rearranged_forBrother62mm'
                pdf.save(f'{outname}.pdf')
                pages = pdf2image.convert_from_path(f'{outname}.pdf', dpi=203)
                for page in pages:
                    page.save(f'{outname}.png', 'PNG')

        case "Hermes_A4":
            c = page.mediabox
            pdf_rearranged = pikepdf.new()
            if opts.format == "Brother_62mm":
                brother = True
                outname = f'{filename}_rearranged_forBrother62mm'
                page_size = [424,176]  # 62mm high and 150mm long

            else:
                brother=False
                outname = f'{filename}_rearranged_for100x150mm'
                page_size = [280,424]  # 100x150mm (standard 4x6" label)

            new_page = pdf_rearranged.add_blank_page(page_size=page_size)
            # rearrangement to fit into 100x150mm (4x6") standard labels
            # or 62mmx150mm Brother endless labels

            # Hermes logo 18 high, 121 wide
            c[0] = 407 # left margin
            c[1] = 782 # lower margin
            c[2] = 528 # right margin
            c[3] = 800 # upper margin
            if brother:
                rect = pikepdf.Rectangle(5,153,126,171)
            else:
                rect = pikepdf.Rectangle(154,400,275,418)
            new_page.add_overlay(page, rect, shrink=True, expand=False)
            # Barcode 185 high, 88 wide
            c[0] = 56 # left margin
            c[1] = 580 # lower margin
            c[2] = 144 # right margin
            c[3] = 765 # upper margin
            if brother:
                rect = pikepdf.Rectangle(331,-4,419,181)
            else:
                rect = pikepdf.Rectangle(5,130,93,315)
            new_page.add_overlay(page, rect, shrink=True, expand=False)
            # Sender 110 high, 100 wide
            c[0] = 273 # left margin
            c[1] = 666 # lower margin
            c[2] = 373 # right margin
            c[3] = 776 # upper margin
            if brother:
                rect = pikepdf.Rectangle(205,100,305,171)
            else:
                rect = pikepdf.Rectangle(5,308,105,418)
            new_page.add_overlay(page, rect, shrink=True, expand=False)
            # Receiver 150 high, 100 wide
            c[0] = 273 # left margin
            c[1] = 480 # lower margin
            c[2] = 373 # right margin
            c[3] = 630 # upper margin
            if brother:
                rect = pikepdf.Rectangle(210,-15,310,100)
            else:
                rect = pikepdf.Rectangle(120,150,220,300)
            new_page.add_overlay(page, rect, shrink=True, expand=False)
            # Routing Code 65 high, 65 wide
            c[0] = 195 # left margin
            c[1] = 565 # lower margin
            c[2] = 260 # right margin
            c[3] = 630 # upper margin
            if brother:
                rect = pikepdf.Rectangle(150,35,200,100)
            else:
                rect = pikepdf.Rectangle(120,50,220,115)
            new_page.add_overlay(page, rect, shrink=True, expand=False)
            # Postage Paid 65 high, 75 wide
            c[0] = 165 # left margin
            c[1] = 465 # lower margin
            c[2] = 240 # right margin
            c[3] = 530 # upper margin
            if brother:
                rect = pikepdf.Rectangle(5,-10,140,35)
            else:
                rect = pikepdf.Rectangle(120,320,195,385)
            new_page.add_overlay(page, rect, shrink=True, expand=False)
            # QR-Code 110 high, 88 wide
            c[0] = 56 # left margin
            c[1] = 460 # lower margin
            c[2] = 144 # right margin
            c[3] = 570 # upper margin
            if brother:
                rect = pikepdf.Rectangle(5,35,140,145)
            else:
                rect = pikepdf.Rectangle(5,20,93,130)
            new_page.add_overlay(page, rect, shrink=True, expand=False)
            # WE DO! Logo 80 high, 55 wide
            c[0] = 470 # left margin
            c[1] = 645 # lower margin
            c[2] = 525 # right margin
            c[3] = 725 # upper margin
            if brother:
                rect = pikepdf.Rectangle(150,100,205,171)
            else:
                rect = pikepdf.Rectangle(220,305,275,385)
            new_page.add_overlay(page, rect, shrink=True, expand=False)

            pdf_rearranged.save(f'{outname}.pdf')
            dpi = 300 if brother else 203
            pages = pdf2image.convert_from_path(f'{outname}.pdf', dpi=dpi)
            for page in pages:
                page.save(f'{outname}.png', 'PNG')

    
