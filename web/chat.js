/* Plain JavaScript, no build step. Responses are always rendered as text. */
(function () {
  "use strict";
  const config = window.KEEKS_CONFIG || {};
  const notes = window.KEEKS_NOTES || [];
  const messages = document.getElementById("messages");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("question");
  const send = document.getElementById("send");
  const clear = document.getElementById("clear");
  const status = document.getElementById("request-status");
  const suggestions = document.getElementById("suggestions");
  let history = [], busy = false;
  let endpoint = "";
  if (config.apiUrl) {
    try {
      const url = new URL(config.apiUrl, location.href);
      if (url.protocol !== "https:" && !["localhost", "127.0.0.1"].includes(url.hostname)) throw new Error("HTTPS required");
      endpoint = url.href;
    } catch (_) { status.textContent = "Invalid model endpoint. Using demo notes."; }
  }
  const connected = Boolean(endpoint);
  if (!connected) document.getElementById("about-mode").textContent = "This demo searches " + notes.length + " authored starter notes, including documentation-informed creative coding examples with source links. GPU training and a model connection are still pending.";
  if (connected) {
    document.getElementById("mode-label").textContent = "Model endpoint configured";
    document.getElementById("mode-disclosure").textContent = "Model mode · messages are sent to the configured server.";
    document.getElementById("about-mode").textContent = "This page is configured to call the model server. The server requires a trained LoRA adapter. Responses can still contain mistakes; check calculations and hardware details.";
  }
  function renderText(container, text) {
    // Parse only fenced code; all content remains inert text, never HTML.
    const chunks = text.split(/(```[\s\S]*?```)/g);
    for (const chunk of chunks) {
      if (chunk.startsWith("```")) {
        const pre = document.createElement("pre"), code = document.createElement("code");
        code.textContent = chunk.replace(/^```[^\n]*\n?/, "").replace(/```$/, "").trim();
        pre.appendChild(code); container.appendChild(pre);
      } else { container.appendChild(document.createTextNode(chunk)); }
    }
  }
  function addSources(article, sources) {
    if (!sources || !sources.length) return;
    const nav = document.createElement("div"); nav.className="note-sources";
    for (const source of sources) {
      try {
        const url = new URL(source.url); if (url.protocol !== "https:") continue;
        const link = document.createElement("a"); link.href=url.href;
        link.textContent=source.title + " ↗"; link.target="_blank"; link.rel="noopener noreferrer";
        nav.appendChild(link);
      } catch (_) { /* Invalid references are never rendered as links. */ }
    }
    article.appendChild(nav); messages.scrollTop=messages.scrollHeight;
  }
  function message(role, text, title, kind) {
    const article = document.createElement("article");
    article.className = "message " + role + (kind ? " " + kind : "");
    const speaker = document.createElement("div"); speaker.className = "speaker";
    speaker.textContent = role === "user" ? "You" : connected ? "Keeks" : "Keeks · demo";
    article.appendChild(speaker);
    if (title) { const t = document.createElement("div"); t.className = "note-title"; t.textContent = title; article.appendChild(t); }
    const bubble = document.createElement("div"); bubble.className = "bubble"; renderText(bubble, text); article.appendChild(bubble);
    messages.appendChild(article); messages.scrollTop = messages.scrollHeight;
    return article;
  }
  function welcome() {
    messages.replaceChildren();
    const article = message("assistant", "Hey, I'm Keeks. Let's turn a curious question into something you can make.", "", "welcome");
    const small = document.createElement("small");
    small.textContent = connected ? "Ask me about sounds, signals, code, physics, or your next synth experiment." : "Try drum synth, TidalCycles, Hydra, TD, Gibber, ChucK, or p5.js. I'm in demo mode while my fine-tuned model gets set up.";
    article.querySelector(".bubble").appendChild(small);
    messages.scrollTop = 0;
  }
  const retrieve = question => window.KEEKS_RETRIEVAL.retrieve(question, notes);
  function setBusy(value) { busy=value;send.disabled=value;clear.disabled=value;input.readOnly=value;suggestions.querySelectorAll("button").forEach(b=>b.disabled=value); }
  async function ask(question) {
    question=question.trim();if(!question||busy||question.length>2000)return;
    message("user",question); history.push({role:"user",content:question});
    input.value="";document.getElementById("counter").textContent="0 / 2000";
    setBusy(true);status.textContent=connected?"Keeks is thinking…":"Searching starter notes…";
    try {
      let answer;
      if (connected) {
        const controller = new AbortController(); const timer = setTimeout(()=>controller.abort(),90000);
        try {
          const response = await fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({messages:history.slice(-7)}),signal:controller.signal});
          if (!response.ok) throw new Error("Model server returned "+response.status);
          const data=await response.json();
          if (data.mode!=="fine-tuned" || typeof data.response!=="string" || !data.response.trim()) throw new Error("Unexpected model response");
          answer=data.response; message("assistant",answer);
          document.getElementById("mode-label").textContent="Fine-tuned model · connected";
          document.getElementById("mode-disclosure").textContent="Fine-tuned model · check calculations and hardware details.";
          document.getElementById("mode-disclosure").classList.add("connected");
        } finally {clearTimeout(timer);}
      } else {
        const note=retrieve(question);
        answer=note?note.answer:"I don't have a matching note yet. Try a tool and task, like ‘Hydra audio’, ‘TD FFT’, ‘ChucK sample’, or ‘drum synth’. This demo retrieves authored notes; it cannot generate a new answer yet.";
        const article = message("assistant",answer,note&&note.prompt?"Starter note: "+note.prompt:"");
        if (note) addSources(article, note.sources);
      }
      history.push({role:"assistant",content:answer});
      history=history.slice(-12);status.textContent="Enter to send · Shift + Enter for a new line";
    } catch (error) {
      history.pop();input.value=question;document.getElementById("counter").textContent=question.length+" / 2000";
      message("assistant","I couldn't reach the model. Your question is back in the box so you can retry. No demo answer has been substituted.","","error");
      status.textContent=error.name==="AbortError"?"Request timed out. Try again shortly.":"Model unavailable. Try again shortly.";
      document.getElementById("mode-label").textContent="Model endpoint · unavailable";
    } finally {setBusy(false);input.focus();}
  }
  form.addEventListener("submit",e=>{e.preventDefault();ask(input.value);});
  input.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey&&!e.isComposing){e.preventDefault();ask(input.value);}});
  input.addEventListener("input",()=>document.getElementById("counter").textContent=input.value.length+" / 2000");
  clear.addEventListener("click",()=>{history=[];welcome();input.value="";document.getElementById("counter").textContent="0 / 2000";status.textContent="New chat started.";input.focus();});
  suggestions.addEventListener("click",e=>{const button=e.target.closest("button[data-question]");if(button)ask(button.dataset.question);});
  const canvas=document.getElementById("wave"), context=canvas.getContext("2d"), frequency=document.getElementById("frequency");
  function draw() {const n=Number(frequency.value);document.getElementById("wave-value").textContent=n.toFixed(1).replace(/\.0$/,"")+" cycles";if(!context)return;context.clearRect(0,0,canvas.width,canvas.height);context.beginPath();for(let x=0;x<=canvas.width;x++){const y=canvas.height/2+Math.sin(x/canvas.width*n*2*Math.PI)*53;if(x===0)context.moveTo(x,y);else context.lineTo(x,y);}context.strokeStyle="#c4f586";context.lineWidth=3;context.stroke();}
  frequency.addEventListener("input",draw);draw();welcome();
})();
