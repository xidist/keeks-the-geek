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
  if (connected) {
    document.getElementById("mode-label").textContent = "Model endpoint configured";
    document.getElementById("mode-disclosure").textContent = "Model mode · messages are sent to the configured server.";
    document.getElementById("about-mode").textContent = "This page is configured to call the model server. The server requires a trained LoRA adapter. Responses can still contain mistakes; check calculations and hardware details.";
  }
  function message(role, text, title, kind) {
    const article = document.createElement("article");
    article.className = "message " + role + (kind ? " " + kind : "");
    const speaker = document.createElement("div"); speaker.className = "speaker";
    speaker.textContent = role === "user" ? "You" : connected ? "Keeks" : "Keeks · demo";
    article.appendChild(speaker);
    if (title) { const t = document.createElement("div"); t.className = "note-title"; t.textContent = title; article.appendChild(t); }
    const bubble = document.createElement("div"); bubble.className = "bubble"; bubble.textContent = text; article.appendChild(bubble);
    messages.appendChild(article); messages.scrollTop = messages.scrollHeight;
    return article;
  }
  function welcome() {
    messages.replaceChildren();
    const article = message("assistant", "Hey, I'm Keeks. Let's turn a curious question into something you can make.", "", "welcome");
    const small = document.createElement("small");
    small.textContent = connected ? "Ask me about sounds, signals, code, physics, or your next synth experiment." : "Pick a rabbit hole below, or search my starter notes. I'm in demo mode while my fine-tuned model gets set up.";
    article.querySelector(".bubble").appendChild(small);
    messages.scrollTop = 0;
  }
  const stop = new Set("a an the is are was were how what why can i me my do does to of in on for and it you your with make making about explain show could should get want know tell some something please help at as from that this".split(" "));
  const aliases = {ffts:"fft",fourier:"fft",synth:"synthesizer",synths:"synthesizer",synthesizers:"synthesizer",drums:"drum",drumheads:"drumhead",signals:"signal",visuals:"visual",graphics:"graphics",coding:"code",coded:"code",programming:"code",guitars:"guitar",oscillators:"oscillator",harmonics:"harmonic"};
  function terms(text) { return (text.toLowerCase().match(/[a-z0-9]+/g)||[]).map(w=>aliases[w]||w).filter(w=>w.length>1&&!stop.has(w)); }
  function retrieve(question) {
    if (/^(hi|hello|hey|hey keeks|hi keeks)[!. ]*$/i.test(question.trim())) return {answer:"Hey! Pick a starter question or name a topic: FFTs, guitar effects, graphics, physics, AI, drums, or Arduino synths."};
    const query = [...new Set(terms(question))];
    if (!query.length) return null;
    let best = null, bestScore = 0;
    for (const note of notes) {
      if (note.prompt.toLowerCase() === question.trim().toLowerCase()) return note;
      const heading = new Set(terms(note.prompt));
      const body = new Set(terms(note.answer));
      let matches = 0;
      let score = query.reduce((sum,w)=>{if(heading.has(w)||body.has(w)) matches++;return sum+(heading.has(w)?4:body.has(w)?1:0);},0);
      score /= Math.sqrt(query.length);
      if (matches < Math.min(2,query.length)) score = 0;
      if (score > bestScore) {bestScore=score;best=note;}
    }
    return bestScore>=2 ? best : null;
  }
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
        answer=note?note.answer:"I don't have a close starter note for that yet. In demo mode I search a small set of notes rather than generate a new answer. Try naming the topic more specifically, or use a question below.";
        message("assistant",answer,note&&note.prompt?"Starter note: "+note.prompt:"");
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
