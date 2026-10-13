"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const RECORD_KEY = "plottwist-free-records-v1", SESSION_KEY = "plottwist-free-session-v1";
  let persistent = true, records = [], session, lead = {}, collecting = false, sequence = 0;
  const newId = () => globalThis.crypto?.randomUUID?.() || `case-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  try { records = JSON.parse(localStorage.getItem(RECORD_KEY) || "[]"); if (!Array.isArray(records)) records = []; session = sessionStorage.getItem(SESSION_KEY) || newId(); sessionStorage.setItem(SESSION_KEY,session); }
  catch { persistent = false; records = []; session = newId(); }
  const ownRecords = () => records.filter(r => r.session_id === session);
  const emailPattern = /[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?)+/i;
  const feedbackPattern = /\b(feedback|complaint|complain|disappointed|unhappy|frustrated|loved|enjoyed|confusing|too hard|too easy|too difficult)\b/i;
  const unknownPattern = /\b(accessib\w*|wheelchair|rain|refund\w*|cancel\w*|discount\w*|available|availability|location|address|parking|allerg\w*|dietary|insurance|payment|pay|opening hours|dogs?|pets?|languages?|age limit|minimum age)\b/i;
  const leadPattern = /\b(book|booking|reserve|reservation|quote|enquiry|inquiry)\b|\b(sign me up|contact me|interested in|plan (?:a|an|my|our)|get in touch)\b|\b(?:i|we) (?:want|need|would like) (?:a|an|our|my) (?:birthday|city|corporate|custom|mystery|event|party)\b/i;
  const generalPattern = /\b(hi|hello|hey|thanks|thank|services?|offer|experiences?|price|pricing|cost|budget|birthday|city|quest|corporate|mission|custom|story|team|aseel|noah|jiso|felix|clue|plottwist|about|who|long|duration|people|guests|group|work|different)\b/i;
  const cancelPattern = /\b(no thanks|never mind|nevermind|stop|cancel|do not save|don't save|skip)\b/i;
  function routeMessage(message) {
    if (collecting && cancelPattern.test(message)) return "lead_collection";
    if (feedbackPattern.test(message) || unknownPattern.test(message)) return "feedback_unanswered";
    if (leadPattern.test(message) || emailPattern.test(message)) return "lead_collection";
    if (collecting && !(message.includes("?") && generalPattern.test(message))) return "lead_collection";
    return generalPattern.test(message) ? "general_question" : "feedback_unanswered";
  }
  function saveRecord(kind, data) {
    const duplicate = ownRecords().find(r => r.kind === kind && JSON.stringify(r.data) === JSON.stringify(data));
    if (duplicate) return {ok:true,id:duplicate.id,kind,status:"already_recorded"};
    const record = {id:newId(),session_id:session,kind,data,created_at:new Date().toISOString()};
    const next = [...records, record];
    if (persistent) {
      try { localStorage.setItem(RECORD_KEY,JSON.stringify(next)); }
      catch { return {ok:false,kind:"storage_error",error:"Browser storage is full or unavailable. The record was not saved."}; }
    }
    records = next; updateCount();
    console.info(`[tool log] ${kind}: ${record.id} (${persistent ? "saved in this browser" : "saved for this page only"})`);
    return {ok:true,id:record.id,kind,status:"saved",storage:persistent ? "browser_local" : "page_memory"};
  }
  function record_customer_interest(email, name, message) {
    if (![email,name,message].every(v => typeof v === "string" && v.trim()) || email.length > 254 || name.length > 120 || message.length > 4000 || !new RegExp(`^(?:${emailPattern.source})$`,"i").test(email)) return {ok:false,kind:"validation_error",error:"Please provide a valid email, your name, and a short enquiry note."};
    return saveRecord("lead",{email:email.toLowerCase(),name,message});
  }
  function record_feedback(question) {
    if (typeof question !== "string" || !question.trim() || question.length > 4000) return {ok:false,kind:"validation_error",error:"Feedback must contain between 1 and 4,000 characters."};
    return saveRecord("feedback",{question});
  }
  function replyGeneral(message) {
    if (/\b(aseel|noah|jiso|felix|who|your team|team members)\b/i.test(message)) return "Meet the people behind the plot: Aseel — Story Director; Noah — Puzzle Architect; Jiso — Experience Producer; Felix — Guest Experience Lead. I’m Clue, your virtual adventure concierge.";
    if (/\b(custom)\b/i.test(message)) return "Custom Story Adventures turn your ideas into a personalized mystery. They are quote-only, with scope and duration agreed with the team. What occasion and story theme do you have in mind?";
    if (/birthday/i.test(message) && !/all|services|offer|compare/i.test(message)) return "Birthday Mystery Nights put the guest of honour inside the story: 6–20 guests, about 2 hours, from USD 240 per group. This is a fictional starting price. Would you like to prepare an enquiry?";
    if (/city/i.test(message) && !/all|services|offer|compare/i.test(message)) return "City Quests are clue-led adventures for 2–12 guests, about 90 minutes, from USD 90 per group. This is a fictional starting price; the actual route and availability need human review.";
    if (/corporate|mission/i.test(message) && !/all|services|offer|compare/i.test(message)) return "Corporate Missions turn collaboration into an adventure: 10–60 guests, about 2.5 hours, from USD 650 per group. This is a fictional starting price. What is your team’s size and occasion?";
    if (/^(hi|hello|hey)[.! ]*$/i.test(message)) return "Welcome to PlotTwist. I’m Clue — your next adventure starts with a good question. What are you imagining?";
    if (/^(thanks|thank you)[.! ]*$/i.test(message)) return "You’re welcome. Every good story starts with a little curiosity.";
    return "You bring the people. We bring the plot.\n\nBirthday Mystery Nights: 6–20 guests · 2 hours · from USD 240/group.\nCity Quests: 2–12 guests · 90 minutes · from USD 90/group.\nCorporate Missions: 10–60 guests · 2.5 hours · from USD 650/group.\nCustom Story Adventures: a tailored story · quote-only.\n\nThese are fictional starting prices. Which adventure should we explore?";
  }
  function respond(message) {
    const route = routeMessage(message);
    const trace = [{stage:"mode",mode:"free_static_browser_demo",model_call:false},{stage:"router",route,method:"three-way heuristic"}];
    let draft;
    if (route === "lead_collection") {
      if (cancelPattern.test(message)) { collecting = false; lead = {}; draft = "Of course. I’ve stopped this enquiry. You can still explore our adventures without leaving contact details."; }
      else {
        collecting = true;
        const email = message.match(emailPattern); if (email) lead.email = email[0];
        const name = message.match(/\b(?:my name is|i am|i'm|i’m)\s+([\p{L}][\p{L} '-]{0,119}?)(?=[,.!\n]|\s+(?:and|my email|please|interested|planning)\b|$)/iu); if (name) lead.name = name[1].trim();
        if (/\b(birthday|city|corporate|custom|mystery|quest|party|event|mission)\b/i.test(message)) lead.message = message;
        const missing = ["name","email","message"].filter(key => !lead[key]);
        if (missing.length) {
          const labels = {name:"your name",email:"your email address",message:"a short note about the experience you want"};
          draft = `Let’s open your story file. Please share ${missing.map(key=>labels[key]).join(", ")}. I’ll save the enquiry in this browser for the demo; it won’t confirm a booking.`;
        } else {
          const args = {...lead}, result = record_customer_interest(args.email,args.name,args.message);
          trace.push({stage:"tool",tool:"record_customer_interest",arguments:args,result,source:"browser_demo"});
          draft = result.ok ? `Your story file is open, ${lead.name}! Your enquiry has been saved ${persistent ? "in this browser" : "for this page"}. Find it in The casebook. This fictional demo does not send email or confirm a booking.` : `I couldn’t save your enquiry. ${result.error}`;
          if (result.ok) { collecting = false; lead = {}; }
        }
      }
    } else if (route === "feedback_unanswered") {
      const result = record_feedback(message);
      trace.push({stage:"tool",tool:"record_feedback",arguments:{question:message},result,source:"browser_demo"});
      const opening = feedbackPattern.test(message) ? "Thank you for sharing that feedback." : "I don’t have a confirmed answer in the business profile, so I won’t guess.";
      draft = result.ok ? `${opening} I’ve saved it ${persistent ? "in this browser" : "for this page"} for demonstration. You can inspect it in The casebook. No message was sent to a real team.` : `${opening} I couldn’t save it: ${result.error}`;
    } else draft = replyGeneral(message);
    let revised = draft;
    if ($("reflection").checked) {
      const checks = ["Rule-based audit; no model call."];
      if (/\bUSD\s*\d|\$\d/.test(draft) && !/fictional/i.test(draft)) { revised += " Prices are fictional starting prices in USD."; checks.push("Added the price qualification."); } else checks.push("Price qualification present or no price quoted.");
      if (collecting && !lead.email && !/email/i.test(revised)) { revised += " What email address should I attach to your local enquiry?"; checks.push("Added the missing email request."); } else checks.push("Missing contact details requested when applicable.");
      trace.push({stage:"reflection",method:"rule_based_browser_demo",draft,revised,changed:revised!==draft,checks});
    }
    return {reply:revised,route,trace};
  }
  function addMessage(role, text) {
    $("welcome")?.remove();
    const item = document.createElement("div"); item.className = `message ${role}`;
    const label = document.createElement("small"); label.textContent = role === "user" ? "YOUR CLUE" : "CLUE / BROWSER DEMO";
    const body = document.createElement("span"); body.textContent = text;
    item.append(label,body); $("conversation").append(item); $("conversation").scrollTop = $("conversation").scrollHeight;
  }
  function renderTrace(result) {
    $("route-label").textContent = result.route.replaceAll("_"," "); $("trace").replaceChildren();
    result.trace.forEach((event,index) => {
      const row = document.createElement("details"); row.className = "trace-row"; row.open = event.stage === "router" || event.stage === "tool";
      const summary = document.createElement("summary"), n = document.createElement("span"); n.textContent = String(index+1).padStart(2,"0"); summary.append(n,document.createTextNode(event.stage.toUpperCase()));
      const pre = document.createElement("pre"); pre.textContent = JSON.stringify(event,null,2); row.append(summary,pre); $("trace").append(row);
    });
  }
  function updateCount() { $("record-count").textContent = String(ownRecords().length); }
  function renderRecords() {
    $("record-list").replaceChildren(); const data = ownRecords();
    if (!data.length) { const empty=document.createElement("div"); empty.className="empty-records"; empty.textContent="No records yet. Start a conversation, save an enquiry, or share feedback."; $("record-list").append(empty); }
    for (const record of data) {
      const card=document.createElement("article"); card.className="record-card";
      const top=document.createElement("div"); top.className="record-top";
      const title=document.createElement("strong"); title.textContent=record.kind === "lead" ? "ENQUIRY / SAVED LOCALLY" : "FEEDBACK / SAVED LOCALLY";
      const time=document.createElement("time"); time.dateTime=record.created_at; time.textContent=new Date(record.created_at).toLocaleString(); top.append(title,time);
      const body=document.createElement("p"); body.textContent=record.kind === "lead" ? `${record.data.name}\n${record.data.email}\n\n${record.data.message}` : record.data.question;
      const ref=document.createElement("small"); ref.textContent=`Reference: ${record.id}`; card.append(top,body,ref); $("record-list").append(card);
    }
    $("records-json").textContent=JSON.stringify(data,null,2);
    $("storage-status").textContent=persistent ? "Stored only in this browser. Refreshing keeps this conversation’s records; New conversation starts another case. Nothing is sent to a server." : "Browser storage is unavailable. Records last only while this page stays open; export them before leaving.";
    updateCount();
  }
  function openTab(id) {
    for (const name of ["concierge","casebook","team"]) { const active=name===id; $(name).hidden=!active; $(`tab-${name}`).setAttribute("aria-selected",String(active)); $(`tab-${name}`).tabIndex=active?0:-1; }
    if (id === "casebook") renderRecords();
  }
  const tabNames=["concierge","casebook","team"];
  tabNames.forEach((id,index)=> { $(`tab-${id}`).addEventListener("click",()=>openTab(id)); $(`tab-${id}`).addEventListener("keydown",event=> { if (!["ArrowRight","ArrowLeft","Home","End"].includes(event.key)) return; event.preventDefault(); const next=event.key==="Home"?0:event.key==="End"?2:(index+(event.key==="ArrowRight"?1:2))%3; openTab(tabNames[next]); $(`tab-${tabNames[next]}`).focus(); }); });
  $("chat-form").addEventListener("submit",event=> { event.preventDefault(); const message=$("prompt").value.trim(); if (!message) return; addMessage("user",message); $("prompt").value=""; const result=respond(message); addMessage("bot",result.reply); renderTrace(result); sequence++; $("prompt").focus(); });
  $("prompt").addEventListener("keydown",event=> { if (event.key==="Enter" && !event.shiftKey) { event.preventDefault(); $("chat-form").requestSubmit(); } });
  document.querySelectorAll("[data-example]").forEach(button=>button.addEventListener("click",()=> { $("prompt").value=button.dataset.example; $("prompt").focus(); }));
  $("refresh-records").addEventListener("click",renderRecords);
  $("export-records").addEventListener("click",()=> { const blob=new Blob([JSON.stringify({mode:"free_static_browser_demo",session_id:session,records:ownRecords()},null,2)],{type:"application/json"}); const url=URL.createObjectURL(blob), link=document.createElement("a"); link.href=url; link.download="plottwist-casebook.json"; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000); });
  $("new-case").addEventListener("click",()=> { session=newId(); try {sessionStorage.setItem(SESSION_KEY,session);}catch{} lead={}; collecting=false; $("conversation").replaceChildren(); addMessage("bot","A fresh case, a new possibility. What kind of mystery are you imagining?"); $("trace").replaceChildren(); $("route-label").textContent="New conversation"; updateCount(); $("prompt").focus(); });
  updateCount();
})();