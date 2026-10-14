"""Local transport contracts with controlled fixtures; real runs are separate."""
import copy,json,tempfile,unittest
from pathlib import Path
from local_client import LocalClient,LocalModelError
from plottwist_agent import PlotTwistAgent

class LocalTests(unittest.TestCase):
    def test_application_boundary_is_labeled_separately_from_model_review(self):
        answers=[{'content':'A birthday starts at USD 240.'},{'content':json.dumps({'revised_reply':'A birthday starts at USD 240.','checks':['Checked.']})}]
        client=LocalClient(transport=lambda _: {'done':True,'message':answers.pop(0)})
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',client=client,db_path=Path(folder)/'data.sqlite3')
            try:result=agent.respond('What is the birthday starting price?')
            finally:agent.store.close()
        self.assertIn('fictional, indicative',result['reply'])
        audit=next(e for e in result['trace'] if e['stage']=='reflection')
        self.assertFalse(audit['changed'])
        self.assertNotIn('fictional',audit['revised'])
        self.assertEqual(result['trace'][-1]['source'],'application_guard')
        answers=[{'tool_calls':[{'function':{'name':'record_feedback','arguments':{'question':'Is wheelchair access confirmed?'}}}]},
                 {'content':'Your question was recorded.'},
                 {'content':json.dumps({'revised_reply':'Your question was recorded.','checks':['Checked.']})}]
        client=LocalClient(transport=lambda _: {'done':True,'message':answers.pop(0)})
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',client=client,db_path=Path(folder)/'data.sqlite3')
            try:
                result=agent.respond('Is wheelchair access confirmed?')
                self.assertEqual(agent.stats()['feedback'],1)
            finally:agent.store.close()
        self.assertIn('do not confirm',result['reply'])
        self.assertEqual(result['trace'][-1]['source'],'application_guard')

    def test_controlled_reflection_labels_draft_and_has_no_side_effects(self):
        requests=[]
        def request(payload):
            requests.append(copy.deepcopy(payload))
            return {'done':True,'message':{'content':json.dumps({'revised_reply':'Indicative starting price is USD 650 per group. No booking or email was made.','checks':['Removed invented price and actions.']})}}
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',client=LocalClient(transport=request),db_path=Path(folder)/'data.sqlite3')
            try:
                result=agent.review_draft('Tell me about Custom Story Adventures.','It costs USD 50. I booked it and emailed you.')
                self.assertEqual(agent.records(),[])
            finally:agent.store.close()
        self.assertNotIn('tools',requests[0])
        self.assertTrue(next(e for e in result['trace'] if e['stage']=='reflection')['changed'])
        self.assertIn('test',next(e for e in result['trace'] if e['stage']=='test_input')['provenance'].lower())

    def test_incomplete_lead_asks_only_missing_fields_without_save_tools(self):
        requests=[]
        def request(payload):
            requests.append(copy.deepcopy(payload));return {'done':True,'message':{'content':'What email should I attach?'}}
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',client=LocalClient(transport=request),db_path=Path(folder)/'data.sqlite3')
            try:
                result=agent.respond('Please save a birthday enquiry. My name is Aseel.',settings={'reflection':False})
                self.assertEqual(agent.records(),[])
            finally:agent.store.close()
        self.assertNotIn('tools',requests[0])
        self.assertIn('missing fields: email',requests[0]['messages'][0]['content'])
        self.assertIn('Aseel',requests[0]['messages'][0]['content'])
        self.assertFalse(any(e['stage']=='tool' for e in result['trace']))

    def test_real_dispatch_and_model_reflection_contract(self):
        requests=[]
        answers=[{'tool_calls':[{'function':{'name':'record_feedback','arguments':{'question':'Is wheelchair access confirmed?'}}}]},
                 {'content':'I saved the question locally.'},
                 {'content':json.dumps({'revised_reply':'I saved your question locally; the team must confirm access.','checks':['Unknown access stated honestly.']})}]
        def request(payload):
            requests.append(copy.deepcopy(payload));return {'done':True,'done_reason':'stop','model':'qwen2.5:3b','eval_count':20,'message':answers.pop(0)}
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',client=LocalClient(transport=request),db_path=Path(folder)/'data.sqlite3')
            try:
                result=agent.respond('Is wheelchair access confirmed?',session_id='local-test')
                self.assertEqual(agent.stats('local-test')['feedback'],1)
            finally:agent.store.close()
        self.assertEqual(result['mode'],'local')
        self.assertEqual(requests[0]['tools'][0]['function']['name'],'record_feedback')
        self.assertEqual(len(requests[0]['tools']),1)
        self.assertEqual(requests[0]['format']['properties']['name']['enum'],['record_feedback'])
        self.assertEqual(requests[1]['messages'][-1]['role'],'tool')
        self.assertEqual(requests[1]['messages'][-1]['tool_name'],'record_feedback')
        self.assertIn('saved',requests[1]['messages'][-1]['content'])
        self.assertNotIn('tools',requests[2])
        self.assertEqual(requests[2]['format']['required'],['revised_reply','checks'])
        event=next(e for e in result['trace'] if e['stage']=='reflection')
        self.assertEqual(event['method'],'model_review');self.assertTrue(event['changed'])
        self.assertEqual(event['generation']['eval_count'],20)
        self.assertEqual(next(e for e in result['trace'] if e['stage']=='tool')['source'],'model')

    def test_local_failure_never_falls_back_to_demo(self):
        def failed(_):raise LocalModelError('Server unavailable',503)
        with tempfile.TemporaryDirectory() as folder:
            agent=PlotTwistAgent(mode='local',client=LocalClient(transport=failed),db_path=Path(folder)/'data.sqlite3')
            try:result=agent.respond('What services do you offer?')
            finally:agent.store.close()
        self.assertEqual(result['mode'],'local');self.assertIn('No offline answer was substituted',result['reply'])
        self.assertEqual(next(e for e in result['trace'] if e['stage']=='reflection')['status'],'skipped_after_error')

    def test_loopback_only_and_truncation(self):
        with self.assertRaises(ValueError):LocalClient(base_url='https://example.com')
        client=LocalClient(transport=lambda _: {'done':True,'done_reason':'length','message':{'content':'partial'}})
        with self.assertRaises(LocalModelError):client.create(model='qwen2.5:3b',messages=[{'role':'user','content':'Hello'}])

    def test_printed_call_is_detected_not_claimed_as_final(self):
        client=LocalClient(transport=lambda _: {'done':True,'message':{'content':'I will save it. {"name":"record_feedback","arguments":{"question":"feedback"}}'}})
        from prompts import TOOL_SCHEMAS
        response=client.create(model='qwen2.5:3b',messages=[{'role':'user','content':'feedback'}],tools=TOOL_SCHEMAS)
        self.assertEqual(response.choices[0].message.tool_calls[0].function.name,'record_feedback')
        self.assertEqual(response.choices[0].message.content,'')
