from dateutil.parser import parse
import pyparsing as pp

makeInt = lambda t: int(t[0])

two_digit = pp.Word(pp.nums, min=1, max=2)
year_digits = pp.Word(pp.nums)
date_sep = pp.oneOf('- /')
date_gram = two_digit + date_sep + two_digit + date_sep + year_digits
date_grammar = pp.SkipTo(pp.Combine(date_gram), include=True)

male_prefix = (pp.CaselessLiteral('m') ^ pp.CaselessLiteral('b')).setParseAction(lambda t: 'male')
female_prefix = (pp.CaselessLiteral('f') ^ pp.CaselessLiteral('g')).setParseAction(lambda t: 'female')

male_grammar = pp.SkipTo(male_prefix + pp.Group(pp.OneOrMore(pp.Word(pp.nums).setParseAction(makeInt))), include=True)
female_grammar = pp.SkipTo(female_prefix + pp.Group(pp.OneOrMore(pp.Word(pp.nums).setParseAction(makeInt))), include=True)


def zero_pad(li, max_len):
    return li + ([0] * (max_len - len(li)))


def parse_report(text):
    male_portion = None
    female_portion = None

    report_data = {}

    try:
        male_portion = male_grammar.parseString(text)

        skip, code, values = male_portion

        report_data[code] = dict(zip(range(1, 5), zero_pad(values[:4], 4)))
    except pp.ParseException:
        pass

    try:
        female_portion = female_grammar.parseString(text)

        skip, code, values = female_portion

        report_data[code] = dict(zip(range(1, 5), zero_pad(values[:4], 4)))
    except pp.ParseException:
        pass

    if not male_portion and not female_portion:
        return None

    return report_data


def parse_date(text):
    try:
        result = date_grammar.parseString(text)
    except pp.ParseException:
        return None

    skip, date_val = result[0]

    return parse(date_val, dayfirst=True)
