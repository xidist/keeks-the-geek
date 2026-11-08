const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const { retrieve } = require('../web/retrieval.js');
const context = {window:{}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../web/notes.js'),'utf8'),context);
const notes=context.window.KEEKS_NOTES;
const cases=[
  ['Drum synth','creative-drum-synth'], ['drum synthesis','creative-drum-synth'],
  ['drum synthesizer','creative-drum-synth'], ['Tidal cycles','creative-tidal-start'],
  ['TidalCycles','creative-tidal-start'], ['Hydra docs','creative-hydra-start'],
  ['Hydra audio','creative-hydra-audio'], ['TD docs','creative-td-start'],
  ['TD FFT','creative-td-spectrum'], ['Touch Designer','creative-td-start'],
  ['Gibber','creative-gibber-start'], ['Gibber drums','creative-gibber-drums'],
  ['ChucK','creative-chuck-start'], ['ChucK sample','creative-chuck-buffer'],
  ['drum sampling','creative-sampling-start'], ['live coding','creative-live-start'],
  ['graphics docs','creative-p5-start'], ['p5.js','creative-p5-start']
];
for(const [query,id] of cases) assert.equal(retrieve(query,notes)?.id,id,query);
for(const note of notes) assert.equal(retrieve(note.prompt,notes)?.id,note.id,note.prompt);
assert.equal(retrieve('Find a sushi restaurant in Minneapolis',notes),null);
assert.equal(retrieve('flight hotel reservations',notes),null);
for(const platform of ['tidal','hydra','td','gibber','chuck']) {
  const result=retrieve(platform+' synth',notes);
  if(result) assert.ok(result.topic===({tidal:'tidalcycles',td:'touchdesigner'}[platform]||platform));
}
console.log(`${cases.length} short queries, ${notes.length} exact notes, unrelated fallbacks and platform boundaries passed.`);
