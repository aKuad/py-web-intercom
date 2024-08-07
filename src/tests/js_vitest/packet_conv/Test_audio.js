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
import { packet_audio_encode, packet_audio_decode, is_audio_packet, AUDIO_PACKET_TYPE_ID } from "../../../static/packet_conv/audio.js"
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
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);

    const raw_packet_invalid_id = Uint8Array.of(0x20, raw_packet.slice(1));
    //                                          ~~~~
    //                                          as non 0x10 or 0x11 byte

    expect(is_audio_packet(raw_packet_invalid_id)).toBe(false);
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
  //   // type checking will be tested in verify_invalid_type
  // });


  test("dec_invalid_value", () => {
    const audio_pcm_org = generate_rand_float32array(ONE_FRAME_SAMPLES);
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array();
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);

    const raw_packet_invalid_id = Uint8Array.of(0x20, raw_packet.slice(1));
    //                                          ~~~~
    //                                          as non 0x10 or 0x11 byte
    const raw_packet_invalid_len = Uint8Array.of(AUDIO_PACKET_TYPE_ID, 0x41, 0x42, 0x43);
    // invalid len - means ext_bytes data missing packet

    expect(() => packet_audio_decode(raw_packet_invalid_id )).toThrowError(new RangeError("Invalid packet, it is not an audio packet"));
    expect(() => packet_audio_decode(raw_packet_invalid_len)).toThrowError(new RangeError("Invalid packet, too short bytes received"));
  });


  test("verify_invalid_type", () => {
    expect(() => packet_audio_decode("")).toThrowError(new TypeError("raw_packet must be Uint8Array"));
    //                           ~~ as non Uint8Array
  });


  test("verify_invalid_value", () => {
    const raw_packet_invalid_empty = new Uint8Array();

    expect(() => is_audio_packet(raw_packet_invalid_empty)).toThrowError(new RangeError("Empty array passed"));
  });
});
