from dr.models import FIELD_MAP
from django.db.models import F, Func, Value, Sum
import pandas as pd

FORMULAS = {
    'general_male': 'BA + BB + BE + BF + BJ + BK + CA + CB + CE + CF + CJ + CK + DA + DB + DE + DF + DJ + DK + EA + EB + EE + EF + EJ + EK',
    'general_female': 'AA + AB + BC + BD + BG + BH + BM + BN + CC + CD + CG + CH + CM + CN + DC + DD + DG + DH + DM + DN + EC + ED + EG + EH + EM + EN',
    'general_certified': 'AA + BA + BC + BE + BG + BJ + BM + CA + CC + CE + CG + CJ + CM + DA + DC + DE + DG + DJ + DM + EA + EC + EE + EG + EJ + EM',
    'general_uncertified': 'AB + BB + BD + BF + BH + BK + BN + CB + CD + CF + CH + CK + CN + DB + DD + DF + DH + DK + DN + EB + ED + EF + EH + EK + EN',
    'general_childbirth': 'AA + AB',
    'general_fevers': 'BA + BB + BC + BD + BE + BF + BG + BH + BJ + BK + BM + BN',
    'general_accidents': 'CA + CB + CC + CD + CE + CF + CG + CH + CJ + CK + CM + CN',
    'general_hiv': 'DA + DB + DC + DD + DE + DF + DG + DH + DJ + DK + DM + DN',
    'general_others': 'EA + EB + EC + ED + EE + EF + EG + EH + EJ + EK + EM + EN',

    'male_1': 'BA + BB + CA + CB + DA + DB + EA + EB',
    'male_4': 'BE + BF + CE + CF + DE + DF + EE + EF',
    'male_5': 'BJ + BK + CJ + CK + DJ + DK + EJ + EK',
    'male_fevers': 'BA + BB + BE + BF + BJ + BK',
    'male_accidents': 'CA + CB + CE + CF + CJ + CK',
    'male_hiv': 'DA + DB + DE + DF + DJ + DK',
    'male_others': 'EA + EB + EE + EF + EJ + EK',

    'female_1': 'BC + BD + CC + CD + DC + DD + EC + ED',
    'female_4': 'BG + BH + CG + CH + DG + DH + EG + EH',
    'female_5': 'BM + BN + CM + CN + DM + DN + EM + EN',
    'female_childbirth': 'AA + AB',
    'female_fevers': 'BC + BD + BG + BH + BM + BN',
    'female_accidents': 'CC + CD + CG + CH + CM + CN',
    'female_hiv': 'DC + DD + DG + DH + DM + DN',
    'female_others': 'EC + ED + EG + EH + EM + EN'
}
extracted_fields = {field: Func(F("data"), Value("$." + field), function="JSON_EXTRACT") for field in FIELD_MAP.keys()}
extracted_fields_sum = {field: Sum(Func(F("data"), Value("$." + field), function="JSON_EXTRACT")) for field in FIELD_MAP.keys()}

def death_report_summary(queryset):
    items = queryset.annotate(
        lga=F('location__name'),
        state=F('location__parent__name'),
        zone=F('location__parent__parent__name'),
        country=F('location__parent__parent__parent__name')
    ).values('country', 'zone', 'state', 'lga').annotate(**extracted_fields_sum)
    df = pd.DataFrame(data=[pd.Series(data=item) for item in items])
    if not df.empty:
        for k in FORMULAS.keys():
            df[k] = df.eval(FORMULAS[k])
    return df
