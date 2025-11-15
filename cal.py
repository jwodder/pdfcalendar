#!/usr/bin/env -S pipx run
# TODO:
# - Implement holiday highlighting
#  - Use the `holidays` package?
# - Handle weekday abbreviations more than one character long
# - Use small caps for month names?
# - Use more `calendar` functions
#  - Use one of the `Calendar` methods instead of `monthrange()`?
# - Add an option for typesetting months in a grid instead of a column?

# /// script
# dependencies = ["attrs >= 18.1", "reportlab ~= 3.4"]
# ///

import calendar
from datetime import date
import attr
from reportlab.lib import pagesizes
from reportlab.pdfgen.canvas import Canvas

# HOLIDAYS = [
#    ('Christmas', lambda year: date(year, 12, 25), (1, 0, 0)),
#    ('Easter',
#    ('Thanksgiving',
# ]


@attr.s
class CalendarColumn:
    canvas = attr.ib()
    font_size = attr.ib()  ### If `None`, use current font size?
    font_name = attr.ib(default=None)  # If `None`, use current font
    firstweekday = attr.ib(default=calendar.SUNDAY)
    month_names = attr.ib(converter=list)  # list of 13 elements
    week_abbrevs = attr.ib(converter=list)  # list of 7 elements; index 0 = Monday
    #: Whether to rotate the month names such that successive letters are
    #: written downwards (`True`) or upwards (`False`)
    month_names_downwards = attr.ib(default=True)
    ###holidays = attr.ib()

    @month_names.validator
    def validate(self, attribute, value):
        if len(value) != 13 or not all(isinstance(x, str) for x in value[1:]):
            raise ValueError(value)

    @month_names.default
    def default(self):
        # set via function so that the current locale is honored
        return list(calendar.month_name)

    @week_abbrevs.validator
    def validate(self, attribute, value):
        if len(value) != 7 or not all(isinstance(x, str) for x in value):
            raise ValueError(value)

    @week_abbrevs.default
    def default(self):
        # set via function so that the current locale is honored
        return [d[:1] for d in calendar.day_name]

    @property
    def height(self):
        """The maximum height of a rendered calendar"""
        return 56 * self.sqsize

    @property
    def width(self):
        return 8 * self.sqsize

    @property
    def sqsize(self):
        return max(
            self.canvas.stringWidth(
                "33",
                fontName=self.font_name,
                fontSize=self.font_size,
            ),
            self.font_size * 1.2,
        )

    def top2bl(self, t):
        """
        Given a y-coordinate (usually the top of a square), return the
        y-coordinate at which text should be drawn so as to appear immediately
        beneath the argument
        """
        return t - self.font_size * (5 / 6)
        # t - sqsize/2 - self.font_size/6
        # t - sqsize/2 - self.font_size/2

    def draw(self, year, x=0, y=0):
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


if __name__ == "__main__":
    import locale

    locale.setlocale(locale.LC_ALL, "")

    start = date.today().year
    qty = 5

    c = Canvas("cal.pdf", pagesizes.letter)
    calcol = CalendarColumn(
        canvas=c,
        font_name="Times-Roman",
        font_size=10,
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
