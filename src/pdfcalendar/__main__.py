from __future__ import annotations
import argparse
from datetime import date
import locale
from reportlab.lib import pagesizes
from reportlab.pdfgen.canvas import Canvas
from . import __version__
from .column import CalendarColumn
from .three_by_four import ThreeByFourCalendar


def main() -> None:
    locale.setlocale(locale.LC_ALL, "")

    parser = argparse.ArgumentParser(
        description="Create a calendar PDF document for one or more years"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    columns_parser = subparsers.add_parser(
        "columns", help="Display each year as a single column of weeks"
    )
    columns_parser.add_argument("--font-name", default="Times-Roman")
    columns_parser.add_argument("--font-size", type=int, default=10)
    columns_parser.add_argument("outfile")

    three_by_four_parser = subparsers.add_parser(
        "three-by-four", help="Display each year as a three-by-four grid of months"
    )
    three_by_four_parser.add_argument("--font-name", default="Times-Roman")
    three_by_four_parser.add_argument("--font-size", type=int, default=14)
    three_by_four_parser.add_argument("outfile")

    args = parser.parse_args()
    this_year = date.today().year

    if args.subcommand == "columns":
        qty = 5
        c = Canvas(args.outfile, pagesizes.letter)
        calcol = CalendarColumn(
            canvas=c,
            font_name=args.font_name,
            font_size=args.font_size,
            month_names_downwards=True,
            # firstweekday=calendar.MONDAY,
        )
        page_width, page_height = pagesizes.letter
        width = calcol.width + calcol.sqsize
        height = calcol.height
        for i in range(qty):
            calcol.draw(
                this_year + i,
                (page_width - qty * width) / 2 + i * width,
                (page_height + height) / 2,
            )
        c.showPage()
        c.save()
    elif args.subcommand == "three-by-four":
        c = Canvas(args.outfile, pagesizes.letter)
        cal = ThreeByFourCalendar(
            canvas=c,
            font_name=args.font_name,
            font_size=args.font_size,
            pagesize=pagesizes.letter,
        )
        cal.draw(this_year)
        c.showPage()
        c.save()
    else:
        raise AssertionError(f"Unhandled subcommand: {args.subcommand!r}")


if __name__ == "__main__":
    main()
