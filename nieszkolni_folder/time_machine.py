from datetime import datetime
from datetime import timedelta
import re


date_today = datetime.today()


class TimeMachine:
    global now_pattern
    global now_pattern_colons
    global now_pattern_colons_2
    global today_pattern
    now_pattern = "%Y-%m-%d %H-%M-%S-%f"
    now_pattern_colons = "%Y-%m-%d %H:%M:%S"
    now_pattern_colons_2 = "%Y-%m-%dT%H:%M"
    today_pattern = "%Y-%m-%d"

    def show_now_pattern(self):
        return now_pattern

    def show_today_pattern(self):
        return today_pattern

    def now(self):
        return datetime.now().strftime(now_pattern)

    def now_colons(self):
        return datetime.now().strftime(now_pattern_colons)

    def today(self):
        return datetime.now().strftime(today_pattern)

    def mondays(self):

        list_of_mondays = []

        for index in range(-30, 91):
            date = date_today + timedelta(days = index)

            if date.isoweekday() == 1:
                list_of_mondays.append(date.strftime("%Y-%m-%d"))
            else:
                pass
        return list_of_mondays

    def x_days_including_today(self, x_days):
        starting_date = (int(x_days) - 1) * -1
        list_of_dates = []

        for index in range(starting_date, 1):
            date = date_today + timedelta(days=index)
            list_of_dates.append(date.strftime("%Y-%m-%d"))

        return list_of_dates

    def extract_day(self, date):
        try:
            self.date = date

            day = re.search("\d\d\d\d\-\d\d\-\d\d", self.date).group()

            return day
        except Exception as e:
            pass

    def date_to_number(self, date):
        if isinstance(date, str):
            end = datetime.strptime(date, today_pattern)
        else:
            end = datetime.strftime(date, today_pattern)
            end = datetime.strptime(end, today_pattern)

        start = "2000-01-01"
        start = datetime.strptime(start, today_pattern)

        difference = end - start
        result_raw = difference.days
        result = int(result_raw)

        return result

    def date_time_to_number(self, date):
        if isinstance(date, str):
            try:
                end = datetime.strptime(date, now_pattern_colons)
            except Exception as e:
                end = datetime.strptime(date, now_pattern_colons_2)

        else:
            end = datetime.strftime(date, now_pattern_colons)
            end = datetime.strptime(end, now_pattern_colons)

        start = "2000-01-01 00:00:00"
        start = datetime.strptime(start, now_pattern_colons)

        difference = end - start
        day_to_seconds = int(difference.days) * 86400
        time_to_seconds = int(difference.seconds)
        difference_seconds = day_to_seconds + time_to_seconds

        return difference_seconds

    def american_to_system_date(self, date):
        try:
            if re.search(r"\d{1,2}\/\d{1,2}\/\d{4}", date) is not None:
                american = datetime.strptime(date, "%m/%d/%Y")
                system = datetime.strftime(american, today_pattern)

                return system

            elif re.search(r"\d{4}-\d{2}-\d{2}", date) is not None:

                return date

            else:
                pass

        except ValueError as error:

            return f"{error}"

    def today_number(self):
        today = self.today()
        today_number = self.date_to_number(today)

        return today_number

    def now_number(self):
        now = self.now_colons()
        now_number = self.date_time_to_number(now)

        return now_number

    def number_to_system_date(self, date_number):
        date_number = int(date_number)
        start = datetime.strptime("2000-01-01", today_pattern)
        difference = timedelta(days=date_number)
        end = start + difference
        date = datetime.strftime(end, today_pattern)

        return date

    def number_to_system_date_time(self, date_time_number):
        start = datetime.strptime("2000-01-01 00:00:00", now_pattern_colons)
        difference = timedelta(seconds=date_time_number)
        end = start + difference
        date_time = datetime.strftime(end, now_pattern_colons)

        return date_time

    def last_sunday(self):
        today = datetime.today()
        weekday = datetime.today().weekday()
        pattern = weekday + 1
        difference = timedelta(days=pattern)
        last_sunday_raw = today - difference
        last_sunday = datetime.strftime(last_sunday_raw, today_pattern)

        return last_sunday

    def this_sunday(self):
        today = datetime.today()
        weekday = datetime.today().weekday()
        pattern = 7 - weekday - 1
        difference = timedelta(days=pattern)
        this_sunday_raw = today + difference
        this_sunday = datetime.strftime(this_sunday_raw, today_pattern)

        return this_sunday

    def next_sunday(self):
        today = datetime.today()
        weekday = datetime.today().weekday()
        pattern = 14 - weekday - 1
        difference = timedelta(days=pattern)
        next_sunday_raw = today + difference
        next_sunday = datetime.strftime(next_sunday_raw, today_pattern)

        return next_sunday

    def academic_week_start(self):
        weekday = datetime.today().isoweekday()

        if weekday > 5:
            academic_week_start = self.this_sunday()
        else:
            academic_week_start = self.last_sunday()

        return academic_week_start

    def academic_week_start_number(self):
        date = self.academic_week_start()
        date_number = self.date_to_number(date)

        return date_number

    def display_sundays(self):
        today = datetime.today()
        weekday = datetime.today().weekday()
        last_day = timedelta(days=105)

        sundays = []

        text = self.academic_week_start()
        number = self.academic_week_start_number()
        default_sunday = (number, text)

        sundays.append(default_sunday)

        for week in range(17, 0, -1):

            pattern = (weekday + 1) + (week * 7)
            difference = timedelta(days=pattern)

            sunday = (today + last_day) - difference
            sunday = datetime.strftime(sunday, today_pattern)

            sunday_number = self.date_to_number(sunday)
            entry = (sunday_number, sunday)

            sundays.append(entry)

        return sundays

    def this_week_number_sign(self):
        year = datetime.now().isocalendar().year
        week = datetime.now().isocalendar().week

        year_short = str(year)[2:4]
        week_sign = f"{year_short}W{week:02d}"

        return week_sign

    def number_to_week_number_sign(self, number):
        date_string = self.number_to_system_date(number)
        date = datetime.strptime(date_string, today_pattern)
        year = date.isocalendar().year
        week = date.isocalendar().week

        year_short = str(year)[2:4]
        week_sign = f"{year_short}W{week:02d}"

        return week_sign

    def number_to_week(self, number):
        date_string = self.number_to_system_date(number)
        date = datetime.strptime(date_string, today_pattern)
        week = date.isocalendar().week

        return week

    def time_number_to_date_number(self, time_number):
        date_number_raw = time_number/86400
        date_number = re.search(r"\d{1,}", str(date_number_raw)).group()

        return date_number

    def month_ago(self):
        today_number = self.today_number()
        month_ago_number = today_number - 30
        month_ago = self.number_to_system_date(month_ago_number)

        return month_ago

    def list_dates(self, start, end):
        start = TimeMachine().date_to_number(start)
        end = TimeMachine().date_to_number(end)

        dates = [TimeMachine().number_to_system_date(date) for date in range(start+1, end+1)]

        return dates