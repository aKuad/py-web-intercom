/**
 * @file Audio data parameters at this system
 *
 * It for avoid magic-number coding. And keep same parameters at all modules.
 *
 * @author aKuad
 */


export const SAMPLE_RATE = 44100;
export const FRAME_DURATION_SEC = 0.1;
export const ONE_FRAME_SAMPLES = 4410;  // = SAMPLE_RATE * FRAME_DURATION_SEC
export const CHANNELS = 1;
export const ONE_SAMPLE_BYTES = 2
