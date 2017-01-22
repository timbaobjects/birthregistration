from dr.models import FIELD_MAP
from django.db.models import F, Func, Value, Sum
import pandas as pd

extracted_fields = {field: Func(F("data"), Value("$." + field), function="JSON_EXTRACT") for field in FIELD_MAP.keys()}
extracted_fields_sum = {field: Sum(Func(F("data"), Value("$." + field), function="JSON_EXTRACT")) for field in FIELD_MAP.keys()}

def death_report_summary(queryset):
    items = queryset.annotate(
        state=F('location__parent__name'),
        zone=F('location__parent__parent__name'),
        country=F('location__parent__parent__parent__name')
    ).values('country', 'zone', 'state').annotate(**extracted_fields_sum)
    return pd.DataFrame(data=[pd.Series(data=item) for item in items])
