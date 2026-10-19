class PCM16Encoder extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.targetRate = options.processorOptions.targetSampleRate || 16000;
    this.frameSize = options.processorOptions.frameSize || 320;
    this.ratio = sampleRate / this.targetRate;
    this.position = 0;
    this.source = [];
    this.output = [];
  }

  process(inputs) {
    const input = inputs[0] && inputs[0][0];
    if (!input) return true;
    for (let i = 0; i < input.length; i += 1) this.source.push(input[i]);
    while (this.position + 1 < this.source.length) {
      const left = Math.floor(this.position);
      const fraction = this.position - left;
      const value = this.source[left] + (this.source[left + 1] - this.source[left]) * fraction;
      this.output.push(Math.max(-1, Math.min(1, value)));
      this.position += this.ratio;
      if (this.output.length >= this.frameSize) {
        const pcm = new Int16Array(this.frameSize);
        for (let i = 0; i < pcm.length; i += 1) {
          const sample = this.output[i];
          pcm[i] = sample < 0 ? sample * 32768 : sample * 32767;
        }
        this.port.postMessage(pcm.buffer, [pcm.buffer]);
        this.output.splice(0, this.frameSize);
      }
    }
    const consumed = Math.floor(this.position);
    if (consumed > 0) {
      this.source.splice(0, consumed);
      this.position -= consumed;
    }
    return true;
  }
}

registerProcessor("pcm16-encoder", PCM16Encoder);

