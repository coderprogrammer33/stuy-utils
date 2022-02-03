# StuyUtils-fork

ThunderRedStar's fork of Anthony Chen's [StuyUtils](https://github.com/achen318/stuy-utils). Is updated for the 2021-22 spring semester and will have full feature set and more soon.

## Install
To download this (updated) module, run ` install git+https://github.com/thunder-red-star/stuy-utils.git`

TODO:
- [x] Implement the new schedules
- [x] Add parsing for TSV
- [ ] Add new Term Days
- [x] Deprecate methods involving Term Days until updates are pushed
- [ ] Add more features 

# Original README:

> Useful functions & utilities for Stuyvesant High School.

To download this module, run `pip install stuy-utils` in the terminal.

To test the module or see example code, navigate to the `tests` directory, then running the files there.

## schedule.convert_to_isoformat(day)

> Convert a date object to an ISO-formatted date string.

Convert a date or datetime object from the datetime library to a string formatted using the ISO 8601 format, while also checking if 'date' is a valid date and if it exists in the data.

### Args

- **day** (Union[*datetime.date*, *datetime.datetime*]): A date or datetime object from the datetime library.

### Raises

- **errors.InvalidDate**: Thrown if the input is not a date or a datetime object.
- **errors.DayNotInData**: Thrown if the inputted day is not in term_days.csv.

### Returns

- str: A date using the ISO 8601 format (yyyy-mm-dd).

## schedule.get_day_info(day)

> Returns information about a given day.

Returns the cycle, period, testing subjects, and any events of a given day. If a category does not apply, an empty string will be returned.

### Args

- **day** (Union[*datetime.date*, *datetime.datetime*]): A date or datetime object from the datetime library.

### Raises

- **errors.InvalidDate**: Thrown if the input is not a date or a datetime object.
- **errors.DayNotInData**: Thrown if the inputted day is not in term_days.csv.

### Returns

- _Info_: A namedtule with fields 'cycle', 'period', 'testing', and 'event'.

## schedule.get_next_school_day(day, always_same)

> Returns when the next school day is.

Returns a date object of the next school day from the given day. The given datetime will be returned as a date if school is still in session.

### Args

- **day** (Union[*datetime.date*, *datetime.datetime*]): A date or datetime object from the datetime library.
- **always_same** (bool, optional): Whether or not to always return the given day if the given day is a school day. Defaults to False.

### Raises

- **errors.InvalidDate**: Thrown if the input is not a date or a datetime object.
- **errors.DayNotInData**: Thrown if the inputted day is not in term_days.csv.

### Returns

- Optional[*datetime.date*]: A date object with the year, month, and day of the next school day.

## schedule.get_bell_schedule(day)

> Returns the bell periods of the next school day.

Returns a dictionary of bell periods of the next school day. If the given day is a school day, then the bell schedule of that day will be returned, even if it is afterschool.

### Args

- **day** (Union[*datetime.date*, *datetime.datetime*]): A date or datetime object from the datetime library.

### Raises

- **errors.InvalidDate**: Thrown if the input is not a date or a datetime object.
- **errors.DayNotInData**: Thrown if the inputted day is not in term_days.csv.

### Returns

- Dict[str, *Time*]: A dictionary of keys of strings of the category name (see data/bell_schedule.csv) and values of Time namedtuple objects with fields 'start' and 'end', which returns a datetime object.

## schedule.get_current_class(day)

> Returns information of the current class.

Returns a tuple of information of the current class, where the first element is a string of the category, such as the class period, and a Time namedtuple object, which includes when said period starts and ends.

### Args

- **day** (Union[*datetime.date*, *datetime.datetime*]): A date or datetime object from the datetime library.

### Raises

- **errors.InvalidDate**: Thrown if the input is not a date or a datetime object.
- **errors.DayNotInData**: Thrown if the inputted day is not in term_days.csv.

### Returns

- Optional[Tuple[str, *Time*]]: A tuple of a string of the category name (see data/bell_schedule.csv), and a Time namedtuple object with fields 'start' and 'end', which returns a datetime object.

## schedule.get_next_class(day)

> Returns information of the next class.

Returns a tuple of information of the next class, where the first element is a string of the category, such as the class period, and a Time namedtuple object, which includes when said period starts and ends.

### Args

- **day** (Union[*datetime.date*, *datetime.datetime*]): A date or datetime object from the datetime library.

### Raises

- **errors.InvalidDate**: Thrown if the input is not a date or a datetime object.
- **errors.DayNotInData**: Thrown if the inputted day is not in term_days.csv.

### Returns

- Optional[Tuple[str, *Time*]]: A tuple of a string of the category name (see data/bell_schedule.csv), and a Time namedtuple object with fields 'start' and 'end', which returns a datetime object.
