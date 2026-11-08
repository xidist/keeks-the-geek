# Creative coding corpus

Checked November 8, 2026. This expansion contains 45 newly authored examples across nine areas (36 train, 9 validation), informed by the official references below. It includes no raw documentation dump. Source versions are living pages unless otherwise stated; check the installed tool version before executing generated code.

The browser demo adds 36 notes, for 84 total. It has no trained model yet. The GPU notebook rebuilds 132 training and 25 validation rows, evaluates the base model, runs a smoke test, trains QLoRA, compares held-out outputs, and exports the adapter and run evidence. No weights have been produced in this update.

| Source | Official / maintainer reference |
| --- | --- |
| TidalCycles patterns | [tidal-patterns](https://tidalcycles.org/docs/reference/patterns/) |
| TidalCycles mini-notation | [tidal-mini](https://tidalcycles.org/docs/reference/mini_notation/) |
| TidalCycles controls | [tidal-controls](https://tidalcycles.org/docs/reference/controls/) |
| TidalCycles overview | [tidal-overview](https://tidalcycles.org/docs/) |
| Hydra sources | [hydra-sources](https://hydra.ojack.xyz/docs/docs/learning/video-synth-basics/src/) |
| Hydra modulation | [hydra-modulation](https://hydra.ojack.xyz/docs/docs/learning/video-synth-basics/modulate/) |
| Hydra audio input | [hydra-audio](https://hydra.ojack.xyz/docs/docs/learning/interactivity/audio/) |
| Hydra outputs | [hydra-outputs](https://hydra.ojack.xyz/docs/docs/learning/video-synth-basics/outputs/) |
| Hydra dynamic parameters | [hydra-functions](https://hydra.ojack.xyz/docs/docs/learning/sequencing/arrow-functions/) |
| TouchDesigner Audio Device In CHOP | [td-input](https://derivative.ca/UserGuide/Audio_Device_In_CHOP) |
| TouchDesigner Audio Spectrum CHOP | [td-spectrum](https://derivative.ca/UserGuide/Audio_Spectrum_CHOP) |
| TouchDesigner Lag CHOP | [td-lag](https://derivative.ca/UserGuide/Lag_CHOP) |
| TouchDesigner CHOP to TOP | [td-texture](https://derivative.ca/UserGuide/CHOP_to_TOP) |
| Gibber instruments reference | [gibber-reference](https://gibber.cc/docs/) |
| Gibber sequencing tutorial | [gibber-sequence](https://github.com/gibber-cc/gibber/blob/main/playground/examples/sequencing.js) |
| Gibber oscillator tutorial | [gibber-osc](https://github.com/gibber-cc/gibber/blob/main/playground/examples/sounddesign_oscillators.js) |
| Gibber envelope tutorial | [gibber-env](https://github.com/gibber-cc/gibber/blob/main/playground/examples/sounddesign_envelopes.js) |
| Gibber sampler tutorial | [gibber-sample](https://github.com/gibber-cc/gibber/blob/main/playground/examples/sampler.js) |
| Gibber graphics tutorial | [gibber-graphics](https://github.com/gibber-cc/gibber/blob/main/playground/examples/graphics.intro.js) |
| ChucK time | [chuck-time](https://chuck.stanford.edu/doc/language/time.html) |
| ChucK basic unit generators | [chuck-ugens](https://chuck.stanford.edu/doc/reference/ugens-basic.html) |
| Web Audio buffer playback | [web-buffer](https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode) |
| Web Audio decoding | [web-decode](https://developer.mozilla.org/en-US/docs/Web/API/BaseAudioContext/decodeAudioData) |
| Web Audio oscillator | [web-osc](https://developer.mozilla.org/en-US/docs/Web/API/OscillatorNode) |
| Web Audio exponential automation | [web-ramp](https://developer.mozilla.org/en-US/docs/Web/API/AudioParam/exponentialRampToValueAtTime) |
| Web Audio sequencing | [web-schedule](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Advanced_techniques) |
| SuperCollider SinOsc | [sc-sine](https://docs.supercollider.online/Classes/SinOsc.html) |
| SuperCollider EnvGen | [sc-envelope](https://docs.supercollider.online/Classes/EnvGen.html) |
| SuperCollider WhiteNoise | [sc-noise](https://docs.supercollider.online/Classes/WhiteNoise.html) |
| p5.js canvas | [p5-canvas](https://p5js.org/reference/p5/createCanvas/) |
| p5.js shader | [p5-shader](https://p5js.org/reference/p5/shader/) |
| p5.js frame duration | [p5-time](https://p5js.org/reference/p5/deltaTime/) |
| p5.js noise | [p5-noise](https://p5js.org/reference/p5/noise/) |

## Next GPU step

Open the repository's Colab notebook, select an available GPU runtime, then run the cells in order. Review the data before training. The environment records real package versions, data hashes, metrics and model revision when available. A completed training run is followed by real base/adapter comparisons; no predicted results are prefilled. Export the adapter ZIP before the session expires.

For the website to generate answers, deploy the included server with the completed adapter, then configure the public HTTPS chat endpoint. The static GitHub Pages frontend cannot run this CUDA training/serving recipe. Keep the demo label until a real server response is verified.
