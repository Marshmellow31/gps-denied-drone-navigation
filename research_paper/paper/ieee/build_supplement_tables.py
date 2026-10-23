"""Additional tables from accepted exports; no scientific recomputation."""
from build_assets import HERE, RESULTS, EVIDENCE, STRATA, LABELS, load, table

def main():
    tolerance, windows = [], []
    for backend, label in [('fastlio','FAST-LIO'),('pointlio','Point-LIO')]:
        a=load(RESULTS/(backend+'_analysis.json'))
        for group, name in zip(STRATA,LABELS):
            for key, tol in [('half_tolerance_recovery','Half'),(None,'Primary'),('double_tolerance_recovery','Double')]:
                if key:
                    d=a[key]['by_stratum'][group]; n=d['recovered_events'];den=d['truth_eligible_events']
                else:
                    cohort=[r for r in a['truth_labels'] if r['stratum']==group]
                    n=sum(r['status']=='RECOVERED' for r in cohort);den=len(cohort)
                tolerance.append([label,name,tol,f'{n}/{den}'])
            for scene in ['corridor','control']:
                d=a['three_second_rate_sensitivity_by_stratum'][group][scene]
                windows.append([label,name,scene,d['events_with_valid_windows'],f"{d['valid_window_count_total']}/{d['planned_window_count_total']}",f"{100*d['equal_event_mean_pass_fraction']:.2f}"])
    table('tolerance_strata','lllr',['Backend','Geometry','Tolerance','Recovered'],tolerance)
    table('window3_strata','lllrrr',['Backend','Geometry','Scene','Events','Valid/planned',r'Pass (\%)'],windows)
    a=load(EVIDENCE/'t14_repeatability_audit.json');data=[]
    for r in a['comparisons']:
        e=r['translation_error_1s_m'];m=r['methods']
        data.append([r['seed'],r['scene'].lower(),f"{e['median_absolute_change']:.4f}",f"{e['maximum_absolute_change']:.4f}",m['FASTLIO_MIN_EIG_G3']['confirmed_state_disagreements_all_ticks'],m['DCREG_SCHUR_MASK']['confirmed_state_disagreements_all_ticks']])
    table('repeatability','rlrrrr',['Seed','Scene','Median change (m)','Maximum (m)','Scalar ticks','Schur ticks'],data)

if __name__=='__main__':main()
