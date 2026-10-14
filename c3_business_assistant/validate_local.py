"""Reproduce the actual local acceptance study; no fixtures or fallback replies."""
from pathlib import Path
import argparse,json,tempfile,time
from plottwist_agent import PlotTwistAgent

CASES=[('business','What does Birthday Mystery Nights include, how long does it last, and what is its starting price?','facts'),
       ('lead_start','Please save an enquiry for a birthday mystery for 10 guests.','lead'),
       ('lead_name','My name is Aseel.','lead'),
       ('lead_email','My email is aseel@example.com.','lead'),
       ('unknown','Do you have confirmed wheelchair access at a venue next Friday?','unknown'),
       ('feedback','The puzzles were too difficult. Please record my feedback.','feedback'),
       ('team','Who are Aseel, Noah, Jiso and Felix on your team?','team')]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',default='qwen2.5:3b')
    parser.add_argument('--output',type=Path,default=Path('data/local-validation.json'))
    args=parser.parse_args()
    with tempfile.TemporaryDirectory() as folder:
        agent=PlotTwistAgent(mode='local',model=args.model,db_path=Path(folder)/'records.sqlite3')
        payload={'mode':'actual_local_llm','model':args.model,'fictional_contact_inputs':True,'runs':[]}
        histories={}
        try:
            for case,message,session in CASES:
                history=histories.setdefault(session,[])
                started=time.perf_counter()
                result=agent.respond(message,history,session_id=session)
                payload['runs'].append({'case':case,'input':message,'history_before':list(history),'elapsed_ms':round((time.perf_counter()-started)*1000,2),**result,'records':agent.records(session)})
                history.extend([{'role':'user','content':message},{'role':'assistant','content':result['reply']}])
                args.output.parent.mkdir(parents=True,exist_ok=True)
                args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
                print(case,result['route'],result['reply'])
            payload['reflection_challenge']=agent.review_draft('Tell me about Custom Story Adventures.','Custom Story Adventures have a guaranteed price of USD 50 per group. I booked the venue and sent an email.')
            args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        finally:agent.store.close()
    failures=[r['case'] for r in payload['runs'] if any(e['stage']=='error' or (e['stage']=='reflection' and e.get('status')!='checked') for e in r['trace'])]
    print('Evidence:',args.output.resolve(),'Runtime failures:',failures)
    return 1 if failures else 0

if __name__=='__main__':raise SystemExit(main())
