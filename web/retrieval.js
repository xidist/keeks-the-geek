/* Authored-note lookup. This does not run or impersonate an LLM. */
(function (root) {
  "use strict";
  const stop = new Set("a an the is are was were how what why can i me my do does to of in on for and it you your with make making about explain show could should get want know tell some something please help at as from that this docs documentation".split(" "));
  const aliases = {ffts:"fft", fourier:"fft", synth:"synthesizer", synths:"synthesizer", synthesizers:"synthesizer", synthesis:"synthesizer", drums:"drum", drumheads:"drumhead", signals:"signal", visuals:"visual", coding:"code", livecoding:"livecode", programming:"code", guitars:"guitar", oscillators:"oscillator", harmonics:"harmonic", td:"touchdesigner", tidal:"tidalcycles", p5js:"p5", samples:"sample", sampling:"sample"};
  function normalize(text) {
    return text.toLowerCase().replace(/c\+\+/g,"cplusplus").replace(/c#/g,"csharp").replace(/\.net/g,"dotnet").replace(/tidal\s+cycles/g,"tidalcycles").replace(/touch\s+designer/g,"touchdesigner").replace(/live\s+coding/g,"livecode").replace(/p5\.js/g,"p5").replace(/[’']/g,"").trim();
  }
  function terms(text) { return (normalize(text).match(/[a-z0-9]+/g)||[]).map(w=>aliases[w]||w).filter(w=>w.length>1&&!stop.has(w)); }
  const platformTopics = new Set(["tidalcycles","hydra","touchdesigner","gibber","chuck"]);
  function retrieve(question, notes) {
    if (/^(hi|hello|hey|hey keeks|hi keeks)[!. ]*$/i.test(question.trim())) return {answer:"Hey! Try drum synth, TidalCycles, Hydra, TD, Gibber, ChucK, sampling, graphics, or FFTs."};
    const exact = notes.find(n => [n.prompt, ...(n.aliases || [])].some(s => normalize(s) === normalize(question)));
    if (exact) return exact;
    const query = [...new Set(terms(question))];
    if (!query.length) return null;
    const requestedPlatforms = query.filter(t=>platformTopics.has(t));
    let best=null, bestScore=0;
    for (const note of notes) {
      // Keep an explicit platform request from returning another language's code.
      if (requestedPlatforms.length === 1 && note.topic !== requestedPlatforms[0] && !terms(note.prompt).includes(requestedPlatforms[0])) continue;
      if ([note.prompt, ...(note.aliases||[])].some(s=>normalize(s)===normalize(question))) return note;
      const heading = new Set(terms(note.prompt + " " + (note.aliases||[]).join(" ")));
      const body = new Set(terms(note.answer));
      let matches=0, headingMatches=0;
      let score=query.reduce((sum,w)=>{
        if (heading.has(w)||body.has(w)) matches++;
        if (heading.has(w)) headingMatches++;
        return sum+(heading.has(w)?4:body.has(w)?1:0);
      },0) / Math.sqrt(query.length);
      if (matches < Math.min(2,query.length) || headingMatches===0 || matches/query.length < 0.35) score=0;
      if (score>bestScore) {bestScore=score;best=note;}
    }
    return bestScore>=2?best:null;
  }
  const api={retrieve,terms};
  if (typeof module!=="undefined" && module.exports) module.exports=api;
  else root.KEEKS_RETRIEVAL=api;
})(typeof window!=="undefined"?window:globalThis);

