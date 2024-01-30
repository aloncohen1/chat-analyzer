from bs4 import BeautifulSoup
import dateutil
from datetime import datetime
import logging
import re
from typing import Optional, Tuple, List, Dict

import pandas as pd

from whatstk.utils.exceptions import RegexError

class HFormatError(Exception):
    """Raised when hformat could not be found."""

    pass

class ColnamesDf:
    """Access class constants using variable ``whatstk.app_utils.app_utils.COLNAMES_DF``.

    Example:
            Access constant ``COLNAMES_DF.DATE``:

            ..  code-block:: python

                >>> from whatstk.app_utils.app_utils import COLNAMES_DF
                >>> COLNAMES_DF.DATE
                'date'

    """

    DATE = "date"
    """Date column"""

    USERNAME = "username"
    """Username column"""

    MESSAGE = "message"
    """Message column"""

    MESSAGE_LENGTH = "message_length"
    """Message length column"""


COLNAMES_DF = ColnamesDf()

COLNAMES_DF = ColnamesDf()


regex_simplifier = {
    "%Y": r"(?P<year>\d{2,4})",
    "%y": r"(?P<year>\d{2,4})",
    "%m": r"(?P<month>\d{1,2})",
    "%d": r"(?P<day>\d{1,2})",
    "%H": r"(?P<hour>\d{1,2})",
    "%I": r"(?P<hour>\d{1,2})",
    "%M": r"(?P<minutes>\d{2})",
    "%S": r"(?P<seconds>\d{2})",
    "%P": r"(?P<ampm>[AaPp].? ?[Mm].?)",
    "%p": r"(?P<ampm>[AaPp].? ?[Mm].?)",
    "%name": rf"(?P<{COLNAMES_DF.USERNAME}>[^:]*)",
}


def parse_telegram_html(data):

    data_list = []

    soup = BeautifulSoup(data, 'html.parser')
    group_name = list(soup.find('div', class_='text bold'))[0].strip()
    for div in soup.select("div.message.default"):
        body = div.find('div', class_='body')
        from_name_ = body.find('div', class_='from_name')
        if from_name_ is not None and from_name_.find('span') is None:
            username = from_name_.string.strip()
            raw_date = body.find('div', class_='date')['title']
            timestamp = dateutil.parser.parse(raw_date)
            links = [l.get('href') for l in body.find_all('a')]

        if body.find('div', class_='media_wrap clearfix') is None:
            text = body.find('div', class_='text').get_text().strip()
        else:
            text = '<Media omitted>'

        data_list.append({"username": username, "date": timestamp, "message": text, "links": links})

    return group_name,pd.DataFrame(data_list)


def _df_from_str(text: str, auto_header: bool = True, hformat: Optional[str] = None, flip_date: bool = False) -> pd.DataFrame:
    # Get hformat
    if hformat:
        # Bracket is reserved character in RegEx, add backslash before them.
        hformat = hformat.replace("[", r"\[").replace("]", r"\]")
    if not hformat and auto_header:
        hformat = extract_header_from_text(text)
        if not hformat:
            raise RuntimeError(
                "Header automatic extraction failed. Please specify the format manually by setting"
                " input argument `hformat`. Report this issue so that automatic header detection support"
                " for your header format is added: https://github.com/lucasrodes/whatstk/issues."
            )
    elif not (hformat or auto_header):
        raise ValueError("If auto_header is False, hformat can't be None.")

    # Generate regex for given hformat
    r, r_x = generate_regex(hformat=hformat)

    # Parse chat to DataFrame
    try:
        df = _parse_chat(text, r, flip_date)
    except RegexError:
        raise HFormatError("hformat '{}' did not match the provided text. No match was found".format(hformat))

    except Exception as e:
        if str(e) == "month must be in 1..12":
            df = _parse_chat(text, r, flip_date=True)
    df = _remove_alerts_from_df(r_x, df)

    df = _add_schema(df)
    return df


def _add_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Add default chat schema to df.

    Args:
        df (pandas.DataFrame): Chat dataframe.

    Returns:
        pandas.DataFrame: Chat dataframe with correct dtypes.

    """
    df = df.astype(
        {
            COLNAMES_DF.DATE: "datetime64[ns]",
            COLNAMES_DF.USERNAME: pd.StringDtype(),
            COLNAMES_DF.MESSAGE: pd.StringDtype(),
        }
    )
    return df

def extract_header_from_text(text: str, encoding: str = "utf-8") -> Optional[str]:
    """Extract header from text.

    Args:
        text (str): Loaded chat as string (whole text).
        encoding (str): Encoding to use for UTF when reading/writing (ex. ‘utf-8’).
                             `List of Python standard encodings
                             <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

    Returns:
        str: Format extracted. None if no header was extracted.

    Example:
            Load a chat using two text files. In this example, we use sample chats (available online, see urls in
            source code :mod:`whatstk.data <whatstk.data>`).

            ..  code-block:: python

                >>> from whatstk.whatsapp.parser import extract_header_from_text
                >>> from urllib.request import urlopen
                >>> from whatstk.data import whatsapp_urls
                >>> filepath_1 = whatsapp_urls.POKEMON
                >>> with urlopen(filepath_1) as f:
                ...     text = f.read().decode('utf-8')
                >>> extract_header_from_text(text)
                '%d.%m.%y, %H:%M - %name:
    """
    # Split lines
    lines = text.split("\n")

    # Get format auto
    try:
        hformat = _extract_header_format_from_lines(lines)
        logging.info("Format found was %s", hformat)
        return hformat
    except Exception as err:  # noqa
        logging.info("Format not found.")
    return None


def _extract_header_format_from_lines(lines: List[str]) -> str:
    """Extract header from list of lines.

    Args:
        lines (list): List of str, each element is a line of the loaded chat.

    Returns:
        str: Format of the header.

    """
    # Obtain header format from list of lines
    elements_list, template_list = _extract_elements_template_from_lines(lines)
    return _extract_header_format_from_components(elements_list, template_list)


def _extract_header_format_from_components(elements_list: List[List[int]], template_list: List[int]) -> str:
    """Extract header format from list containing elements and list containing templates.

    Args:
        elements_list (list): List with component list.
        template_list (list): List with template strings.

    Returns:
        str: Header format.

    """
    # Remove outliers
    elements_list_ = []
    template_list_ = []
    lengths = [len(e) for e in elements_list]
    types = ["".join([str(type(ee).__name__) for ee in e]) for e in elements_list]
    len_mode = max(set(lengths), key=lengths.count)
    type_mode = max(set(types), key=types.count)
    for e, t in zip(elements_list, template_list):
        if (len(e) == len_mode) and ("".join([str(type(ee).__name__) for ee in e]) == type_mode):
            elements_list_.append(e)
            template_list_.append(t)
    # Get positions
    df = pd.DataFrame(elements_list_)
    # dates_df = df.select_dtypes(int)
    dates_df = df.select_dtypes("number")
    template = template_list[0]

    if "%p" in template:
        hour_code = "%I"
    else:
        hour_code = "%H"

    # day
    day_pos = ((dates_df.max() > 27) & (dates_df.max() < 32)).idxmax()
    dates_df = dates_df.drop(columns=[day_pos])
    # year
    # year_pos = dates_df.std().idxmin()
    pos = [0, 1, 2]
    pos.remove(day_pos)
    year_pos = dates_df[pos].max().idxmax()  # Only consider positions 0,1,2
    dates_df = dates_df.drop(columns=[year_pos])
    # Month
    month_pos = dates_df.columns.min()
    dates_df = dates_df.drop(columns=[month_pos])
    # Hour
    hour_pos = 3
    dates_df = dates_df.drop(columns=[hour_pos])
    # Minute
    minutes_pos = 4
    dates_df = dates_df.drop(columns=[minutes_pos])
    # Dictionary with positions and date element code
    dates_pos = {day_pos: "%d", year_pos: "%y", month_pos: "%m", hour_pos: hour_code, minutes_pos: "%M"}
    # Seconds
    if dates_df.shape[1] > 0:
        seconds_pos = 5
        dates_pos[seconds_pos] = "%S"

    keys_ordered = sorted(dates_pos.keys())
    dates_codes = [dates_pos[k] for k in keys_ordered]

    codes = dates_codes + ["%name"]
    # print(codes)
    # print(template)
    # print(template)
    # print(codes)
    code_template = template.format(*codes)
    # print(code_template)
    # print('---------------')
    # print(code_template)
    return code_template

def _extract_elements_template_from_lines(lines: str) -> Tuple[List[List[int]], List[str]]:
    """Get elements_list and template_list from lines.

    Args:
        lines (list): List with messages.

    Returns:
        tuple: elements_list (list), template_list (list)

    """
    # Obtain header format from list of lines
    elements_list = []
    template_list = []
    for line in lines:
        header = _extract_possible_header_from_line(line)
        if header:
            try:
                elements, template = _extract_header_parts(header)
            except RegexError:
                continue
            elements_list.append(elements)
            template_list.append(template)
    return elements_list, template_list


def _extract_header_parts(header: str) -> Tuple[List[int], str]:
    """Extract all parts from header (i.e. date elements and name).

    Args:
        header (str): Header.

    Returns:
        tuple: Contains two elements, (i) list with components and (ii) string template which specifies the formatting
                of the components.

    """

    def _get_last_idx_digit(v: str, i: int) -> int:
        if i + 1 < len(v):
            if v[i + 1].isdigit():
                return _get_last_idx_digit(v, i + 1)
        return i

    # def get_last_idx_alpha(v, i):
    #     if i+1 < len(v):
    #         if v[i+1].isalpha():
    #             return get_last_idx_alpha(v, i+1)
    #         elif i+2 < len(v):
    #             if v[i+1].isspace() and v[i+2].isalpha():
    #                 return get_last_idx_alpha(v, i+2)
    #     return i

    hformat_elements = []
    hformat_template = ""
    i = 0
    while i < len(header):
        if header[i].isdigit():
            j = _get_last_idx_digit(header, i)
            hformat_elements.append(int(header[i: j + 1]))
            hformat_template += "{}"
            i = j
        else:
            if header[i] in ["[", "]"]:
                hformat_template += "\\" + header[i]
            else:
                hformat_template += header[i]
        i += 1
    items = re.findall(r"[-|\]]\s[^:]*:", hformat_template)
    if len(items) != 1:
        raise RegexError(
            "Username match was not possible. Check that header (%s) is of format '... - %name:' or '[...] %name:'",
            hformat_template,
        )
    hformat_template = hformat_template.replace(items[0][2:-1], "%name")
    code = " %p"
    hformat_template = (
        hformat_template.replace(" PM", code)
        .replace(" AM", code)
        .replace(" A.M.", code)
        .replace(" P.M.", code)
        .replace(" am", code)
        .replace(" pm", code)
        .replace(" a.m.", code)
        .replace(" p.m.", code)
    )
    return hformat_elements, hformat_template

def generate_regex(hformat: str) -> Tuple[str, str]:
    r"""Generate regular expression from hformat.

    Args:
        hformat (str): Simplified syntax for the header, e.g. ``'%y-%m-%d, %H:%M:%S - %name:'``.

    Returns:
        str: Regular expression corresponding to the specified syntax.

    Example:
        Generate regular expression corresponding to ``'hformat=%y-%m-%d, %H:%M:%S - %name:'``.

        ..  code-block:: python

            >>> from whatstk.whatsapp.parser import generate_regex
            >>> generate_regex('%y-%m-%d, %H:%M:%S - %name:')
            ('(?P<year>\\d{2,4})-(?P<month>\\d{1,2})-(?P<day>\\d{1,2}), (?P<hour>\\d{1,2}):(?P<minutes>\\d{2}):(?
            P<seconds>\\d{2}) - (?P<username>[^:]*): ', '(?P<year>\\d{2,4})-(?P<month>\\d{1,2})-(?P<day>\\d{1,2}), (?
            P<hour>\\d{1,2}):(?P<minutes>\\d{2}):(?P<seconds>\\d{2}) - ')

    """
    items = re.findall(r"\%\w*", hformat)
    for i in items:
        hformat = hformat.replace(i, regex_simplifier[i])

    hformat = hformat + " "
    hformat_x = hformat.split("(?P<username>[^:]*)")[0]
    return hformat, hformat_x


def _parse_chat(text: str, regex: str, flip_date: bool) -> pd.DataFrame:
    """Parse chat using given regex.

    Args:
        text (str) Whole log chat text.
        regex (str): Regular expression

    Returns:
        pandas.DataFrame: DataFrame with messages sent by users, index is the date the messages was sent.

    Raises:
        RegexError: When provided regex could not match the text.

    """
    result = []
    headers = list(re.finditer(regex, text))
    for i in range(len(headers)):
        try:
            line_dict = _parse_line(text, headers, i, flip_date)
        except KeyError:
            raise RegexError("Could not match the provided regex with provided text. No match was found.")
        result.append(line_dict)
    df_chat = pd.DataFrame.from_records(result)
    df_chat = df_chat[[COLNAMES_DF.DATE, COLNAMES_DF.USERNAME, COLNAMES_DF.MESSAGE]]
    return df_chat


def _parse_line(text: str, headers: List[str], i: int, flip_date: bool) -> Dict[str, str]:
    """Get date, username and message from the i:th intervention.

    Args:
        text (str): Whole log chat text.
        headers (list): All headers.
        i (int): Index denoting the message number.

    Returns:
        dict: i:th date, username and message.

    """
    result_ = headers[i].groupdict()

    if flip_date:
        result_['year'],  result_['month'], result_['day'] = result_['month'], result_['day'], result_['month']
    if "ampm" in result_:
        hour = int(result_["hour"])
        mode = result_.get("ampm").lower()
        if hour == 12 and mode == "am":
            hour = 0
        elif hour != 12 and mode == "pm":
            hour += 12
    else:
        hour = int(result_["hour"])

    # Check format of year. If year is 2-digit represented we add 2000
    if len(result_["year"]) == 2:
        year = int(result_["year"]) + 2000
    else:
        year = int(result_["year"])

    if "seconds" not in result_:
        date = datetime(
            year,
            int(result_["month"]),
            int(result_["day"]),
            hour,
            int(result_["minutes"]),
        )
    else:
        date = datetime(
            year,
            int(result_["month"]),
            int(result_["day"]),
            hour,
            int(result_["minutes"]),
            int(result_["seconds"]),
        )
    username = result_[COLNAMES_DF.USERNAME]
    message = _get_message(text, headers, i)
    line_dict = {
        COLNAMES_DF.DATE: date,
        COLNAMES_DF.USERNAME: username,
        COLNAMES_DF.MESSAGE: message,
    }
    return line_dict


def _get_message(text: str, headers: List[str], i: int) -> str:
    """Get i:th message from text.

    Args:
        text (str): Whole log chat text.
        headers (list): All headers.
        i (int): Index denoting the message number.

    Returns:
        str: i:th message.

    """
    msg_start = headers[i].end()
    msg_end = headers[i + 1].start() if i < len(headers) - 1 else headers[i].endpos
    msg = text[msg_start:msg_end].strip()
    return msg

def _remove_alerts_from_df(r_x: str, df: pd.DataFrame) -> pd.DataFrame:
    """Try to get rid of alert/notification messages.

    Args:
        r_x (str): Regular expression to detect whatsapp warnings.
        df (pandas.DataFrame): DataFrame with all interventions.

    Returns:
        pandas.DataFrame: Fixed version of input dataframe.

    """
    df_new = df.copy()
    df_new.loc[:, COLNAMES_DF.MESSAGE] = df_new[COLNAMES_DF.MESSAGE].apply(lambda x: _remove_alerts_from_line(r_x, x))
    return df_new

def _remove_alerts_from_line(r_x: str, line_df: str) -> str:
    """Remove line content that is not desirable (automatic alerts etc.).

    Args:
        r_x (str): Regula expression to detect WhatsApp warnings.
        line_df (str): Message sent as string.

    Returns:
        str: Cleaned message string.

    """
    if re.search(r_x, line_df):
        return line_df[: re.search(r_x, line_df).start()]
    else:
        return line_df

def _extract_possible_header_from_line(line: str) -> str:
    """Given a `line` extract possible header. Uses ':' as separator.

    Args:
        line (str): Line containing header and message body.

    Returns:
        str: Possible header.

    """
    # Extract possible header from line
    line_split = line.split(": ")
    if len(line_split) >= 2:
        # possible header
        header = line_split[0]
        if not header.isprintable():
            header = header.replace("\u200e", "").replace("\u202e", "")
        if header != '':
            if header[-1] != ":":
                header += ":"
        return header
    return None