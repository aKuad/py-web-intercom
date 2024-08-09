/**
 * @file Tests for `packet_conv/audio.js` module
 *
 * Test cases:
 *   * Can encode/decode audio packet
 *   * Raise TypeError if invalid argument type is passed
 *   * Raise RangeError if invalid argument value is passed
 *
 * Test steps:
 *   * Run this script by vitest - `npm test`
 *
 * @author aKuad
 */

import { describe, test, expect } from "vitest"

import { ONE_FRAME_SAMPLES } from "../../../static/packet_conv/AUDIO_PARAM.js"
import { packet_audio_encode, packet_audio_decode, is_audio_packet } from "../../../static/packet_conv/audio.js"
import { generate_rand_float32array } from "../util/rand_f32a.js"
import { is_almost_equal_float32array } from "../util/almost_eq_f32a.js"


const ERR_INT16_AND_FLOAT32 = 1 / 32767;


describe("true_cases", () => {
  test("enc_dec_verify_ext", () => {
    const audio_pcm_org = generate_rand_float32array(ONE_FRAME_SAMPLES);
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array([1,2,3,4]);
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);
    const [audio_pcm_prc, lane_name_prc, ext_bytes_prc] = packet_audio_decode(raw_packet);

    expect(is_audio_packet(raw_packet)).toBe(true);
    expect(is_almost_equal_float32array(audio_pcm_org, audio_pcm_prc, ERR_INT16_AND_FLOAT32)).toBe(true);
    expect(lane_name_prc).toBe(lane_name_org);
    expect(ext_bytes_prc).toStrictEqual(ext_bytes_org);
  });


  test("enc_dec_verify_noext", () => {
    const audio_pcm_org = generate_rand_float32array(ONE_FRAME_SAMPLES);
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array();
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);
    const [audio_pcm_prc, lane_name_prc, ext_bytes_prc] = packet_audio_decode(raw_packet);

    expect(is_audio_packet(raw_packet)).toBe(true);
    expect(is_almost_equal_float32array(audio_pcm_org, audio_pcm_prc, ERR_INT16_AND_FLOAT32)).toBe(true);
    expect(lane_name_prc).toBe(lane_name_org);
    expect(ext_bytes_prc).toStrictEqual(ext_bytes_org);
  });


  test("enc_dec_verify_silent_ext", () => {
    const audio_pcm_org = generate_rand_float32array(ONE_FRAME_SAMPLES).map(e => e * 0.1);  // Apply gain -20[dB] = 10 ** (-20/20) = 0.1
    const silent_pcm = new Float32Array(ONE_FRAME_SAMPLES); // Zeros array
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array([1,2,3,4]);
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);
    const [audio_pcm_prc, lane_name_prc, ext_bytes_prc] = packet_audio_decode(raw_packet);

    expect(is_audio_packet(raw_packet)).toBe(true);
    expect(audio_pcm_prc).toStrictEqual(silent_pcm);
    expect(lane_name_prc).toBe(lane_name_org);
    expect(ext_bytes_prc).toStrictEqual(ext_bytes_org);
  });


  test("enc_dec_verify_silent_noext", () => {
    const audio_pcm_org = generate_rand_float32array(ONE_FRAME_SAMPLES).map(e => e * 0.1);  // Apply gain -20[dB] = 10 ** (-20/20) = 0.1
    const silent_pcm = new Float32Array(ONE_FRAME_SAMPLES); // Zeros array
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array();
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);
    const [audio_pcm_prc, lane_name_prc, ext_bytes_prc] = packet_audio_decode(raw_packet);

    expect(is_audio_packet(raw_packet)).toBe(true);
    expect(audio_pcm_prc).toStrictEqual(silent_pcm);
    expect(lane_name_prc).toBe(lane_name_org);
    expect(ext_bytes_prc).toStrictEqual(ext_bytes_org);
  });


  test("verify_ng", () => {
    const audio_pcm_org = generate_rand_float32array(ONE_FRAME_SAMPLES);
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array();
    const raw_packet_correct = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);
    const audio_pcm_silent_org = new Float32Array(ONE_FRAME_SAMPLES);
    const raw_packet_silent_correct = packet_audio_encode(audio_pcm_silent_org, lane_name_org, ext_bytes_org);

    const raw_packet_invalid_empty                  = new Uint8Array();
    const raw_packet_invalid_id                     = Uint8Array.of(0x20, ...raw_packet_correct.slice(1)); // 0x20 as non 0x10 or 0x11 byte
    const raw_packet_invalid_no_extlen              = raw_packet_correct.slice(0, 4);
    const raw_packet_invalid_audio_too_short        = raw_packet_correct.slice(0, -1);
    const raw_packet_invalid_audio_too_long         = Uint8Array.of(...raw_packet_correct, 0);  // 0 as an over length byte
    const raw_packet_invalid_silent_audio_too_short = raw_packet_silent_correct.slice(0, -1);
    const raw_packet_invalid_silent_audio_too_long  = Uint8Array.of(...raw_packet_silent_correct, 0); // 0 as an over length byte

    expect(is_audio_packet("")                                       ).toBe(false); // string "" as non Uint8Array
    expect(is_audio_packet(raw_packet_invalid_empty)                 ).toBe(false);
    expect(is_audio_packet(raw_packet_invalid_id)                    ).toBe(false);
    expect(is_audio_packet(raw_packet_invalid_no_extlen)             ).toBe(false);
    expect(is_audio_packet(raw_packet_invalid_audio_too_short)       ).toBe(false);
    expect(is_audio_packet(raw_packet_invalid_audio_too_long)        ).toBe(false);
    expect(is_audio_packet(raw_packet_invalid_silent_audio_too_short)).toBe(false);
    expect(is_audio_packet(raw_packet_invalid_silent_audio_too_long) ).toBe(false);

    expect(() => is_audio_packet(""                                       , true)).toThrowError(new TypeError ("raw_packet must be Uint8Array")); // string "" as non Uint8Array
    expect(() => is_audio_packet(raw_packet_invalid_empty                 , true)).toThrowError(new RangeError("Empty array passed"));
    expect(() => is_audio_packet(raw_packet_invalid_id                    , true)).toThrowError(new RangeError("It is not an audio packet or silent audio packet"));
    expect(() => is_audio_packet(raw_packet_invalid_no_extlen             , true)).toThrowError(new RangeError("Too short bytes received, external bytes length missing"));
    expect(() => is_audio_packet(raw_packet_invalid_audio_too_short       , true)).toThrowError(new RangeError("Too short bytes as audio packet"));
    expect(() => is_audio_packet(raw_packet_invalid_audio_too_long        , true)).toThrowError(new RangeError("Too long bytes as audio packet"));
    expect(() => is_audio_packet(raw_packet_invalid_silent_audio_too_short, true)).toThrowError(new RangeError("Too short bytes received, external bytes length missing"));
    expect(() => is_audio_packet(raw_packet_invalid_silent_audio_too_long , true)).toThrowError(new RangeError("Too long bytes as silent audio packet"));
  });
});


describe("err_cases", () => {
  test("enc_invalid_type", () => {
    const audio_pcm = generate_rand_float32array(ONE_FRAME_SAMPLES);
    const lane_name = "ABC";
    const ext_bytes = new Uint8Array([1,2,3,4]);

    expect(() => packet_audio_encode("", lane_name, ext_bytes)).toThrowError(new TypeError("audio_pcm must be Float32Array"));
    //                               ~~ as non Float32Array
    expect(() => packet_audio_encode(audio_pcm,  1, ext_bytes)).toThrowError(new TypeError("lane_name must be string"));
    //                                           ~ as non string
    expect(() => packet_audio_encode(audio_pcm, lane_name, "")).toThrowError(new TypeError("ext_bytes must be Uint8Array"));
    //                                                     ~~ as non Uint8Array
  });


  test("enc_invalid_value", () => {
    const audio_pcm = generate_rand_float32array(ONE_FRAME_SAMPLES);
    const lane_name = "ABC";
    const ext_bytes = new Uint8Array([1,2,3,4]);

    const lane_name_non_ascii = "🗒";
    const lane_name_over_len = "ABCD";
    const ext_bytes_over_len = new Uint8Array(256);

    expect(() => packet_audio_encode(audio_pcm, lane_name_non_ascii, ext_bytes)).toThrowError(new RangeError("For lane_name, non ascii characters are not allowed"));
    expect(() => packet_audio_encode(audio_pcm, lane_name_over_len , ext_bytes)).toThrowError(new RangeError("For lane_name, over 3 characters string is not allowed"));
    expect(() => packet_audio_encode(audio_pcm, lane_name, ext_bytes_over_len )).toThrowError(new RangeError("For ext_bytes, over 255 bytes data is not allowed"));
  });


  // test("dec_invalid_type", () => {
  //   // packet verification integrated to `is_audio_packet` tests
  // });

  // test("dec_invalid_value", () => {
  //   // packet verification integrated to `is_audio_packet` tests
  // });

  // test("verify_invalid_type", () => {
  //   // no error cases of `is_audio_packet`
  // });

  // test("verify_invalid_value", () => {
  //   // no error cases of `is_audio_packet`
  // });
});
