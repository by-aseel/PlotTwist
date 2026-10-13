# Accessible Gradio presentation layer for the PlotTwist coursework.
from __future__ import annotations
import html
import json
import os
from pathlib import Path
import tempfile
import uuid
import gradio as gr
from plottwist_agent import build_agent

ROOT = Path(__file__).resolve().parent
IS_LAB = True

def esc(value):
    return html.escape(str(value))

def render_trace(events):
    if not events:
        return '<div class="empty-trace"><span class="orbit">◎</span><b>The evidence starts here.</b><p>Send a message to see the route, actions, and observations.</p></div>'
    rows = []
    for i, event in enumerate(events):
        label = str(event.get('stage', event.get('event', event.get('type', 'step'))))
        body = {k: v for k, v in event.items() if k not in ('stage', 'event', 'type')}
        rows.append(f'<details class="trace-step" {"open" if i < 3 else ""}><summary><span>{i+1:02}</span>{esc(label.replace("_", " "))}</summary><pre>{esc(json.dumps(body, ensure_ascii=False, indent=2, default=str))}</pre></details>')
    return '<div class="trace-timeline">' + ''.join(rows) + '</div>'

def brand(mode):
    tag = 'THE PERSONA LAB / CHAPTER 04' if IS_LAB else 'EXPERIENCES WITH A SECRET / CHAPTER 03'
    runtime = 'LIVE AI · GEMINI' if mode == 'live' else 'OFFLINE DEMO · SCRIPTED'
    return f'<div class="brandbar"><div class="wordmark">plot<span>twist</span><i>®</i></div><span class="brand-note">{tag}</span><span class="runtime"><b></b>{runtime}</span></div>'

def hero():
    if IS_LAB:
        return '''<section class="hero lab-hero"><div class="hero-copy"><div class="eyebrow">ONE MYSTERY. THREE MINDS.</div><h1>A different mind.<br>A different <em>twist.</em></h1><p>Meet the advisor, the analyst, and the imagination.<br>Change the persona. Follow the actions. Compare the outcome.</p><div class="hero-meta"><span>01 / CONFIGURE</span><span>02 / INVESTIGATE</span><span>03 / COMPARE</span></div></div><div class="orbital" aria-hidden="true"><div class="orbital-ring ring-one"></div><div class="orbital-ring ring-two"></div><div class="orbital-ring ring-three"></div><div class="core">P<span>T</span><small>AGENT<br>OBSERVATORY</small></div><div class="satellite sat-one">CLUE<small>THE ADVISOR</small></div><div class="satellite sat-two">CIPHER<small>THE ANALYST</small></div><div class="satellite sat-three">MUSE<small>THE CREATIVE</small></div><span class="orbit-coordinate">REASON → ACT → OBSERVE</span></div></section>'''
    return '''<section class="hero"><div class="hero-copy"><div class="eyebrow">YOUR ORDINARY PLANS HAVE BEEN COMPROMISED.</div><h1>Make a memory.<br>Leave a <em>mystery.</em></h1><p>Birthday conspiracies. City secrets. Team missions.<br>You bring the people. We write you into the story.</p><div class="hero-meta"><span>PERSONAL STORIES</span><span>SHARED DISCOVERIES</span><span>UNEXPECTED ENDINGS</span></div></div><div class="dossier-art" aria-hidden="true"><div class="dossier-back"></div><div class="case-card"><div class="case-kicker">PLOT TWIST / EXPERIENCE BUREAU</div><div class="case-number">CASE<br><b>003</b></div><svg class="maze" viewBox="0 0 160 160" fill="none"><circle cx="80" cy="80" r="70" stroke="currentColor" stroke-width="2" stroke-dasharray="325 115" transform="rotate(25 80 80)"/><circle cx="80" cy="80" r="53" stroke="currentColor" stroke-width="2" stroke-dasharray="235 100" transform="rotate(160 80 80)"/><circle cx="80" cy="80" r="35" stroke="currentColor" stroke-width="2" stroke-dasharray="145 76" transform="rotate(40 80 80)"/><path d="M80 80h70M80 80V26M80 80l-49 49" stroke="currentColor" stroke-width="2"/><circle cx="80" cy="80" r="8" fill="currentColor"/></svg><div class="case-bottom">THE MAIN CHARACTER?<br><strong>IT COULD BE YOU.</strong></div></div><div class="ticket"><span>ADMIT ONE<br>UNEXPECTED YOU</span><b>↗</b></div><div class="stamp">OPEN<br>FOR<br>ADVENTURE</div></div></section>'''

def services():
    items = [('01', 'Birthday<br>Mystery Nights', 'An invitation. A secret. Your people.', '6–20 guests · 2 hours', '$240'), ('02', 'City<br>Quests', 'Turn the everyday into a trail of clues.', '2–12 guests · 90 minutes', '$90'), ('03', 'Corporate<br>Missions', 'Different strengths. One shared mission.', '10–60 guests · 2.5 hours', '$650'), ('04', 'Custom Story<br>Adventures', 'A world written around your story.', 'A bespoke brief, built together', 'Bespoke')]
    cards = ''.join(f'<article class="experience-card"><div class="card-number">{n}<span>↗</span></div><h3>{title}</h3><p>{desc}</p><div class="card-detail">{size}</div><div class="card-price">{price}<small>{" / group, from" if price != "Bespoke" else " / quote on request"}</small></div></article>' for n,title,desc,size,price in items)
    return '<section class="experience-section"><div class="section-heading"><span class="eyebrow">CHOOSE YOUR PLOT</span><span>FOUR WAYS IN. COUNTLESS WAYS TO REMEMBER.</span></div><div class="experience-grid">'+cards+'</div><p class="fine-print">Fictional coursework business. Starting prices in USD are illustrative; final scope and availability require human review.</p></section>'

def team():
    people = [('A', 'Aseel', 'Story Director', 'Turns your occasion into a world worth stepping into.'), ('N', 'Noah', 'Puzzle Architect', 'Connects curious minds with satisfying discoveries.'), ('J', 'Jiso', 'Experience Producer', 'Brings the story, the setting, and the people together.'), ('F', 'Felix', 'Guest Experience Lead', 'Makes the first hello feel like part of the adventure.')]
    return '<div class="team-grid">'+''.join(f'<article class="team-card"><span class="team-initial">{initial}</span><h3>{name}</h3><small>{role}</small><p>{desc}</p></article>' for initial,name,role,desc in people)+'</div>'

def records_for(agent, session):
    if hasattr(agent, 'records'):
        return agent.records(session)
    if hasattr(agent, 'store') and hasattr(agent.store, 'records'):
        return agent.store.records(session)
    return []

def create_app(mode=None):
    agent = build_agent(mode=mode or os.getenv('PLOTTWIST_MODE','auto'))
    theme = gr.themes.Base(primary_hue='lime' if not IS_LAB else 'violet', neutral_hue='stone', font=[gr.themes.Font('Arial')], font_mono=[gr.themes.Font('Consolas')]).set(
        body_background_fill='#f4f1e9' if not IS_LAB else '#101210',
        body_background_fill_dark='#f4f1e9' if not IS_LAB else '#101210',
        body_text_color='#20271f' if not IS_LAB else '#eff0df',
        body_text_color_dark='#20271f' if not IS_LAB else '#eff0df',
        block_background_fill='#fcfaf5' if not IS_LAB else '#191c18',
        block_background_fill_dark='#fcfaf5' if not IS_LAB else '#191c18',
        input_background_fill='#ffffff' if not IS_LAB else '#111410',
        input_background_fill_dark='#ffffff' if not IS_LAB else '#111410',
        button_primary_background_fill='#243429' if not IS_LAB else '#d1ff78',
        button_primary_background_fill_dark='#243429' if not IS_LAB else '#d1ff78',
        button_primary_text_color='#faffec' if not IS_LAB else '#182012',
        button_primary_text_color_dark='#faffec' if not IS_LAB else '#182012',
    )
    css = (ROOT/'assets'/'style.css').read_text(encoding='utf-8')
    with gr.Blocks(title='PlotTwist · Persona Lab' if IS_LAB else 'PlotTwist · Mystery Concierge', theme=theme, css=css, analytics_enabled=False) as demo:
        gr.HTML(brand(agent.mode))
        gr.HTML(hero())
        if not IS_LAB:
            gr.HTML(services())
        with gr.Tabs(elem_id='main-tabs'):
            with gr.Tab('The investigation' if IS_LAB else 'Meet your concierge', id='concierge'):
                gr.HTML('<div class="chapter-heading"><span class="eyebrow">'+('THE EXPERIMENT DESK' if IS_LAB else 'THE CONVERSATION STARTS HERE')+'</span><h2>'+('Choose a mind. Open a case.' if IS_LAB else 'A little curiosity goes a long way.')+'</h2></div>')
                with gr.Row(equal_height=False):
                    if IS_LAB:
                        with gr.Column(scale=3, min_width=260, elem_classes='control-panel'):
                            gr.HTML('<div class="panel-label">01 / AGENT CONFIGURATION</div>')
                            persona = gr.Radio([('Clue · the advisor','clue'),('Cipher · the analyst','cipher'),('Muse · the creative','muse')],value='clue',label='Who is on the case?')
                            persona_note = gr.Markdown('**Clue** helps guests find their best-fit experience with warmth and focused questions.')
                            reasoning = gr.Radio([('Direct','direct'),('Brief plan','brief_plan')],value='brief_plan',label='Response approach')
                            examples = gr.Radio([('Zero-shot','zero_shot'),('Few-shot','few_shot')],value='few_shot',label='Worked examples')
                            instruction_role = gr.Radio([('System','system'),('In-message','user')],value='system',label='Instruction placement')
                            with gr.Accordion('Sampling controls',open=False):
                                temperature = gr.Slider(0,2,value=.45,step=.05,label='Temperature')
                                top_p = gr.Slider(.1,1,value=1,step=.05,label='Top-p')
                                top_k = gr.Slider(1,64,value=40,step=1,label='Top-k')
                                frequency = gr.Slider(-2,2,value=.15,step=.05,label='Frequency penalty')
                                presence = gr.Slider(-2,2,value=0,step=.1,label='Presence penalty')
                                max_tokens = gr.Slider(128,2048,value=700,step=32,label='Maximum output tokens')
                            gr.Markdown('In offline demo mode, these controls demonstrate configuration wiring; they do not simulate measured LLM performance.',elem_classes='microcopy')
                    with gr.Column(scale=7,min_width=280):
                        chat = gr.Chatbot(type='messages',label='Case conversation',height=440,show_label=False,placeholder='<div class="chat-welcome"><div class="welcome-symbol">✳</div><h3>Every good story starts<br>with a question.</h3><p>Tell me who’s coming, what you’re celebrating,<br>or what kind of mystery you have in mind.</p></div>',elem_id='plot-chat',allow_tags=False)
                        textbox = gr.Textbox(placeholder='I’m planning a birthday mystery for 12 people…',show_label=False,container=False,scale=7,max_lines=4,submit_btn='Send clue ↗',stop_btn=True)
                        route = gr.Markdown('**Ready** · Waiting for your first clue.',render=False)
                        trace = gr.HTML(render_trace([]),render=False)
                        if not IS_LAB:
                            reflection = gr.Checkbox(value=True,label='Check the reply before sending (reflection)',render=False)
                        def execute(message, history, request, settings):
                            sid=request.session_hash
                            if not sid:
                                raise gr.Error('Your browser session expired. Refresh the page and try again.')
                            result=agent.respond(message,history=history,session_id=sid,settings=settings)
                            return result['reply'], render_trace(result.get('trace',[])), '**'+str(result.get('route','general')).replace('_',' ').title()+'** · '+('Live Gemini' if result.get('mode')=='live' else 'Scripted offline demo')
                        if IS_LAB:
                            def respond(message,history,persona,reasoning,examples,instruction_role,temperature,top_p,top_k,frequency,presence,max_tokens,request:gr.Request):
                                settings=dict(persona=persona,reasoning=reasoning,examples=examples,instruction_role=instruction_role,temperature=temperature,top_p=top_p,top_k=top_k,frequency_penalty=frequency,presence_penalty=presence,max_tokens=max_tokens)
                                return execute(message,history,request,settings)
                        else:
                            def respond(message,history,reflection,request:gr.Request):
                                return execute(message,history,request,{'reflection':bool(reflection)})
                        extra = [persona,reasoning,examples,instruction_role,temperature,top_p,top_k,frequency,presence,max_tokens] if IS_LAB else [reflection]
                        interface=gr.ChatInterface(fn=respond,chatbot=chat,textbox=textbox,type='messages',additional_inputs=extra,additional_outputs=[trace,route],additional_inputs_accordion='Reply settings',submit_btn='Send clue ↗',save_history=False,autofocus=False,api_name='chat')
                        gr.Examples(examples=[[s] for s in ['What adventures do you offer?', 'I want a birthday mystery for 12 people.', 'The puzzles were too difficult.', 'Are your City Quests wheelchair accessible?']],inputs=[textbox],cache_examples=False,label='Start with a clue')
                        with gr.Accordion('Latest activity',open=True,elem_id='activity-panel'):
                            route.render()
                            trace.render()
                    if not IS_LAB:
                        with gr.Column(scale=3,min_width=250,elem_classes='concierge-aside'):
                            gr.HTML('<div class="agent-badge"><span>c.</span><small>YOUR ADVENTURE CONSULTANT</small><h3>Meet Clue.</h3><p>Part curious guide. Part story matchmaker. Here to help your next gathering become something unexpected.</p><div class="capability">01 <b>Find your experience</b></div><div class="capability">02 <b>Capture your event brief</b></div><div class="capability">03 <b>Make your feedback count</b></div><div class="agent-footnote">No spoilers. Just possibilities.</div></div>')
                if IS_LAB:
                    def preset(key):
                        from personas import PERSONAS
                        p=PERSONAS[key]
                        config=p.get('config',p.get('llm_config',{})) if isinstance(p,dict) else {}
                        defaults={'clue':(.45,1,40,0,0,700),'cipher':(.1,1,40,0,0,700),'muse':(.85,1,40,.2,.3,900)}
                        values=defaults[key]
                        notes={'clue':'**Clue** helps guests choose an experience with warmth and focused questions.','cipher':'**Cipher** checks group size, budget, and constraints with precision.','muse':'**Muse** develops imaginative story concepts while keeping proposals separate from confirmed services.'}
                        return notes[key], *[config.get(k,v) for k,v in zip(['temperature','top_p','top_k','frequency_penalty','presence_penalty','max_tokens'],values)]
                    persona.change(preset,inputs=persona,outputs=[persona_note,temperature,top_p,top_k,frequency,presence,max_tokens],api_name=False)
            if IS_LAB:
                with gr.Tab('Persona studio',id='studio'):
                    gr.HTML('<div class="chapter-heading"><span class="eyebrow">SAME BRIEF / THREE PERSPECTIVES</span><h2>Let the personalities speak.</h2><p>Compare fresh conversations with each persona’s default settings.</p></div>')
                    duel_prompt = gr.Textbox(value='We have 12 friends and a $300 starting budget. Suggest a birthday mystery and explain the next step.',label='The shared brief',lines=3)
                    compare = gr.Button('Run the comparison ↗',variant='primary')
                    with gr.Row():
                        duel_outputs=[gr.Markdown('### '+name+'\nWaiting for a brief.',elem_classes='duel-result') for name in ['Clue / Advisor','Cipher / Analyst','Muse / Creative']]
                    def duel(prompt,request:gr.Request):
                        sid=request.session_hash
                        results=[]
                        for p in ['clue','cipher','muse']:
                            result=agent.respond(prompt,history=[],session_id=sid+'-compare-'+p+'-'+uuid.uuid4().hex[:8],settings={'persona':p})
                            results.append('### '+p.title()+'\n\n'+result['reply']+'\n\n---\n*'+('Live model response' if result['mode']=='live' else 'Scripted demo response — not experimental evidence')+'*')
                        return results
                    compare.click(duel,inputs=[duel_prompt],outputs=duel_outputs,api_name='compare_personas')
                    gr.Markdown('For controlled experiments, use `python experiments.py --mode live`. The runner saves raw answers, tool traces, configuration, and metrics. Human ratings of helpfulness and naturalness should be entered after reviewing the answers.')
            with gr.Tab('The casebook',id='casebook'):
                gr.HTML('<div class="chapter-heading"><span class="eyebrow">YOUR SESSION / YOUR RECORDS</span><h2>Good details deserve a paper trail.</h2><p>Enquiries and feedback appear here after a successful tool call.</p></div>')
                refresh=gr.Button('Refresh this casebook ↻',variant='secondary')
                records=gr.JSON(value=[],label='Saved records for this browser session')
                def refresh_casebook(request:gr.Request):
                    return records_for(agent,request.session_hash)
                refresh.click(refresh_casebook,inputs=[],outputs=records,api_name=False)
                export=gr.Button('Export this casebook ↓')
                download=gr.File(label='Download JSON',interactive=False)
                def export_casebook(request:gr.Request):
                    sid=request.session_hash
                    directory=ROOT/'data'/'exports'
                    directory.mkdir(parents=True,exist_ok=True)
                    output=directory/(uuid.uuid4().hex+'.json')
                    output.write_text(json.dumps(records_for(agent,sid),ensure_ascii=False,indent=2,default=str),encoding='utf-8')
                    return str(output)
                export.click(export_casebook,inputs=[],outputs=download,api_name=False)
                gr.Markdown('Records are stored locally in SQLite. Refreshing the browser starts a new session; earlier records remain in the local database. Use fictional contact details when demonstrating the project.')
            with gr.Tab('Behind the plot',id='business'):
                gr.HTML('<div class="chapter-heading"><span class="eyebrow">THE PEOPLE BEHIND THE POSSIBILITIES</span><h2>Small team. Expansive imaginations.</h2></div>')
                gr.HTML(team())
                gr.Markdown('**Our mission:** turn ordinary gatherings into memorable adventures through storytelling and collaborative problem solving. Every experience starts with the group’s occasion, interests, and needs.')
                if IS_LAB:
                    gr.HTML(services())
                gr.Markdown('**A promise about the details:** we use the fictional business profile as our source. Dates, final quotes, venue arrangements, languages, and accessibility accommodations require review by the team. Recording an enquiry does not confirm a booking.')
                gr.File(value=str(ROOT/'me'/'about_business.pdf'),label='Download the business dossier',interactive=False)
        gr.HTML('<footer class="plot-footer"><span class="wordmark">plot<span>twist</span></span><span>A LITTLE CURIOSITY CHANGES EVERYTHING.</span><span>EECE 503P/798S · '+('C4' if IS_LAB else 'C3')+'</span></footer>')
    return demo
