from __future__ import annotations
import calendar
import attrs
from reportlab.pdfgen.canvas import Canvas

YEAR_LABEL_SCALE = 5


@attrs.define
class ThreeByFourCalendar:
    canvas: Canvas

    font_name: str

    font_size: float

    pagesize: tuple[float, float]

    firstweekday: calendar.Day = calendar.SUNDAY

    #: list of 13 elements
    month_names: list[str] = attrs.field(converter=list)

    #: list of 7 elements; index 0 = Monday
    week_abbrevs: list[str] = attrs.field(converter=list)

    cal: calendar.Calendar = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.cal = calendar.Calendar(self.firstweekday)

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

    def top2bl(self, t: float, scale: float = 1.0) -> float:
        """
        Given a y-coordinate (usually the top of a square), return the
        y-coordinate at which text should be drawn so as to appear immediately
        beneath the argument
        """
        return t - self.font_size * scale * (5 / 6)

    def draw(self, year: int) -> None:
        sqsize = max(
            self.canvas.stringWidth(
                "33", fontName=self.font_name, fontSize=self.font_size
            ),
            self.font_size * 1.2,
        )
        months = list(calendar.Month)
        month_rows = [months[i : i + 4] for i in range(0, len(months), 4)]
        week_qtys = [
            max(self.weeks_in_month(year, m) for m in row) for row in month_rows
        ]
        width = sqsize * 7 * 4
        year_label_height = self.font_size * YEAR_LABEL_SCALE * 1.2
        height = year_label_height + sqsize * (6 + sum(week_qtys))
        x = (self.pagesize[0] - width) / 2
        y = (self.pagesize[1] + height) / 2

        self.canvas.setFont(self.font_name, self.font_size * YEAR_LABEL_SCALE)
        # Year label:
        self.canvas.drawCentredString(
            x + width / 2, self.top2bl(y, scale=YEAR_LABEL_SCALE), str(year)
        )
        self.canvas.setFont(self.font_name, self.font_size)
        for i, row in enumerate(month_rows):
            label_top_rule = (
                y - year_label_height - sqsize * (2 * i + sum(week_qtys[:i]))
            )
            for j, m in enumerate(row):
                ulx = x + 7 * j * sqsize
                uly = label_top_rule - 2 * sqsize
                # Month label:
                self.canvas.drawCentredString(
                    ulx + 3.5 * sqsize,
                    self.top2bl(label_top_rule),
                    self.month_names[m],
                )
                for k, wd in enumerate(self.cal.iterweekdays()):
                    # Weekday label:
                    self.canvas.drawCentredString(
                        ulx + k * sqsize + sqsize / 2,
                        self.top2bl(label_top_rule - sqsize),
                        self.week_abbrevs[wd],
                    )
                    if k > 0:
                        self.canvas.setStrokeGray(0.8)
                        # Vrule to left of weekday:
                        self.canvas.line(
                            ulx + k * sqsize,
                            label_top_rule - sqsize,
                            ulx + k * sqsize,
                            uly,
                        )
                        self.canvas.setStrokeGray(0)
                for weekno, week in enumerate(self.cal.monthdays2calendar(year, m)):
                    for d, wd in week:
                        if d != 0:
                            wd = (wd - self.firstweekday) % 7
                            # Day label:
                            self.canvas.drawCentredString(
                                ulx + wd * sqsize + sqsize / 2,
                                self.top2bl(uly - weekno * sqsize),
                                str(d),
                            )
                            self.canvas.setStrokeGray(0.8)
                            # Box around day:
                            self.canvas.rect(
                                ulx + wd * sqsize,
                                uly - weekno * sqsize,
                                sqsize,
                                -sqsize,
                            )
                            self.canvas.setStrokeGray(0)
                if j > 0:
                    # Vrule to left of month:
                    self.canvas.line(
                        ulx, label_top_rule, ulx, uly - sqsize * week_qtys[i]
                    )
            # Hrule above month labels:
            self.canvas.line(x, label_top_rule, x + width, label_top_rule)
            # Hrule between month labels and weekday labels:
            self.canvas.line(
                x, label_top_rule - sqsize, x + width, label_top_rule - sqsize
            )
            # Hrule below weekday labels:
            self.canvas.line(
                x, label_top_rule - 2 * sqsize, x + width, label_top_rule - 2 * sqsize
            )
        # Box around calendar:
        self.canvas.rect(x, y, width, -height)

    def weeks_in_month(self, year: int, month: calendar.Month) -> int:
        return len(self.cal.monthdatescalendar(year, month))
