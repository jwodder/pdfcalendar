from __future__ import annotations
import argparse
import calendar
from datetime import date
import locale
import attrs
from reportlab.lib import pagesizes
from reportlab.pdfgen.canvas import Canvas
from . import __version__


@attrs.define
class CalendarColumn:
    canvas: Canvas

    font_size: float

    #: If `None`, use current font
    font_name: str | None = None

    firstweekday: calendar.Day = calendar.SUNDAY

    #: list of 13 elements
    month_names: list[str] = attrs.field(converter=list)

    #: list of 7 elements; index 0 = Monday
    week_abbrevs: list[str] = attrs.field(converter=list)

    #: Whether to rotate the month names such that successive letters are
    #: written downwards (`True`) or upwards (`False`)
    month_names_downwards: bool = True

    @month_names.validator
    def _month_names_validator(
        self, _attrib: attrs.Attribute, value: list[str]
    ) -> None:
        if len(value) != 13:
            raise ValueError(value)

    @month_names.default
    def _month_names_default(self) -> list[str]:
        # set via function so that the current locale is honored
        return list(calendar.month_name)

    @week_abbrevs.validator
    def _week_abbrevs_validator(
        self, _attrib: attrs.Attribute, value: list[str]
    ) -> None:
        if len(value) != 7:
            raise ValueError(value)

    @week_abbrevs.default
    def _week_abbrevs_default(self) -> list[str]:
        # set via function so that the current locale is honored
        return [d[:1] for d in calendar.day_name]

    @property
    def height(self) -> float:
        """The maximum height of a rendered calendar"""
        return 56 * self.sqsize

    @property
    def width(self) -> float:
        return 8 * self.sqsize

    @property
    def sqsize(self) -> float:
        return max(
            self.canvas.stringWidth(
                "33",
                fontName=self.font_name,
                fontSize=self.font_size,
            ),
            self.font_size * 1.2,
        )

    def top2bl(self, t: float) -> float:
        """
        Given a y-coordinate (usually the top of a square), return the
        y-coordinate at which text should be drawn so as to appear immediately
        beneath the argument
        """
        return t - self.font_size * (5 / 6)
        # t - sqsize/2 - self.font_size/6
        # t - sqsize/2 - self.font_size/2

    def draw(self, year: int, x: float = 0, y: float = 0) -> None:
        # x,y: upper-left corner of calendar to render
        self.canvas.saveState()
        if self.font_name is not None:
            self.canvas.setFont(self.font_name, self.font_size)
        else:
            self.canvas.setFontSize(self.font_size)

        # Weekday of Jan 1 where 0 ≡ self.firstweekday:
        wd1 = (calendar.weekday(year, 1, 1) - self.firstweekday) % 7
        weeks = 53 + bool(calendar.isleap(year) and wd1 == 6)

        sqsize = self.sqsize
        ulx = x + sqsize
        uly = y - sqsize * 2

        self.canvas.setStrokeGray(0.8)
        for i in range(weeks + 1):
            self.canvas.line(
                ulx,
                uly - i * sqsize,
                ulx + 7 * sqsize,
                uly - i * sqsize,
            )
        for i in range(8):
            self.canvas.line(
                ulx + i * sqsize,
                uly + sqsize,
                ulx + i * sqsize,
                uly - sqsize * weeks,
            )

        self.canvas.setStrokeGray(0)
        self.canvas.rect(ulx, uly + sqsize * 2, sqsize * 7, -sqsize * (weeks + 2))
        self.canvas.rect(ulx - sqsize, uly, sqsize, -sqsize * weeks)
        self.canvas.drawCentredString(
            ulx + sqsize * 3.5,
            self.top2bl(uly + sqsize * 2),
            str(year),
        )
        self.canvas.line(ulx, uly + sqsize, ulx + 7 * sqsize, uly + sqsize)

        cal = calendar.Calendar(firstweekday=self.firstweekday)
        for i, wk in enumerate(cal.iterweekdays()):
            self.canvas.drawCentredString(
                ulx + sqsize * (i + 0.5),
                self.top2bl(uly + sqsize),
                self.week_abbrevs[wk],
            )

        cy = uly
        wd = wd1
        self.canvas.line(ulx, uly, ulx + 7 * sqsize, uly)
        if wd == 0:
            monthY = cy
        else:
            monthY = cy - sqsize
            p = self.canvas.beginPath()
            p.moveTo(ulx - sqsize, monthY)
            p.lineTo(ulx + wd * sqsize, monthY)
            p.lineTo(ulx + wd * sqsize, monthY + sqsize)
            self.canvas.drawPath(p, fill=0, stroke=1)
        for mon in range(1, 13):
            _, days = calendar.monthrange(year, mon)
            for d in range(1, days + 1):
                self.canvas.drawCentredString(
                    ulx + sqsize * (wd + 0.5),
                    self.top2bl(cy),
                    str(d),
                )
                wd += 1
                if wd >= 7:
                    wd = 0
                    cy -= sqsize
            if wd == 0:
                my2 = cy
                self.canvas.line(ulx - sqsize, cy, ulx + 7 * sqsize, cy)
            else:
                my2 = cy - sqsize
                p = self.canvas.beginPath()
                p.moveTo(ulx - sqsize, my2)
                p.lineTo(ulx + wd * sqsize, my2)
                p.lineTo(ulx + wd * sqsize, my2 + sqsize)
                p.lineTo(ulx + 7 * sqsize, my2 + sqsize)
                self.canvas.drawPath(p, fill=0, stroke=1)
            self.canvas.saveState()
            if self.month_names_downwards:
                θ = -90
                tx = self.top2bl(ulx)
            else:
                θ = 90
                tx = -self.top2bl(-(ulx - sqsize))
            self.canvas.translate(tx, (monthY + my2) / 2)
            self.canvas.rotate(θ)
            self.canvas.drawCentredString(0, 0, self.month_names[mon])
            self.canvas.restoreState()
            monthY = my2
        self.canvas.restoreState()


def main() -> None:
    locale.setlocale(locale.LC_ALL, "")

    parser = argparse.ArgumentParser(
        description="Create a multiyear calendar PDF document"
    )
    parser.add_argument("--font-name", default="Times-Roman")
    parser.add_argument("--font-size", type=int, default=10)
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("outfile")
    args = parser.parse_args()

    start = date.today().year
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
    # width = 110
    # height = 680
    width = calcol.width + calcol.sqsize
    height = calcol.height

    for i in range(qty):
        calcol.draw(
            start + i,
            (page_width - qty * width) / 2 + i * width,
            (page_height + height) / 2,
        )
    c.showPage()
    c.save()


if __name__ == "__main__":
    main()
