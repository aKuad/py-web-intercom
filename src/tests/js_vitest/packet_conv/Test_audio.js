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

import { packet_audio_encode, packet_audio_decode, is_audio_packet, AUDIO_PACKET_TYPE_ID } from "../../../static/packet_conv/audio.js"
import { describe, test, expect } from "vitest"

const ERR_INT16_AND_FLOAT32 = 1 / 32767;


describe("true_cases", () => {
  test("enc_dec_verify_with_ext", () => {
    const audio_pcm_org = part_testdata_rand_float32array();
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array([1,2,3,4]);
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);
    const [audio_pcm_prc, lane_name_prc, ext_bytes_prc] = packet_audio_decode(raw_packet);

    expect(is_audio_packet(raw_packet)).toBe(true);
    expect(part_is_equal_f32a(audio_pcm_org, audio_pcm_prc, ERR_INT16_AND_FLOAT32)).toBe(true);
    expect(lane_name_prc).toBe(lane_name_org);
    expect(ext_bytes_prc).toStrictEqual(ext_bytes_org);
  });


  test("enc_dec_verify_without_ext", () => {
    const audio_pcm_org = part_testdata_rand_float32array();
    const lane_name_org = "ABC";
    const ext_bytes_org = new Uint8Array();
    const raw_packet = packet_audio_encode(audio_pcm_org, lane_name_org, ext_bytes_org);
    const [audio_pcm_prc, lane_name_prc, ext_bytes_prc] = packet_audio_decode(raw_packet);

    expect(is_audio_packet(raw_packet)).toBe(true);
    expect(part_is_equal_f32a(audio_pcm_org, audio_pcm_prc, ERR_INT16_AND_FLOAT32)).toBe(true);
    expect(lane_name_prc).toBe(lane_name_org);
    expect(ext_bytes_prc).toStrictEqual(ext_bytes_org);
  });


  test("verify_ng", () => {
    const raw_packet_invalid_id = Uint8Array.of(0x11, 0x41, 0x42, 0x43, 0x00, ...part_testdata_rand_float32array());
    //                                          ~~~~  ~~~~~~~~~~~~~~~~
    //                                           |     as string "ABC"
    //                                          as non 0x10 byte

    expect(is_audio_packet(raw_packet_invalid_id)).toBe(false);
  });
});


describe("err_cases", () => {
  test("enc_invalid_type", () => {
    const audio_pcm = part_testdata_rand_float32array();
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
    const audio_pcm = part_testdata_rand_float32array();
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
    const raw_packet_invalid_id = Uint8Array.of(0x11, 0x41, 0x42, 0x43, 0x00, ...part_testdata_rand_float32array());
    //                                          ~~~~  ~~~~~~~~~~~~~~~~
    //                                           |     as string "ABC"
    //                                          as non 0x10 byte
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


/**
 * Generate a random `Float32Array` 4410 length
 *
 * It can use for test data as random audio.
 *
 * @returns {Float32Array} Random array
 */
function part_testdata_rand_float32array() {
  return Float32Array.from(new Array(4410), e => (Math.random() - 0.5) * 2);
  // - 0.5   --> Random number range is [ -0.5, 0.5)
  // * 2     -->                        [   -1,   1)
}


/**
 * Compare two Float32Array objects with allowing specified error
 *
 * Converting between float32 and int16, it includes error.
 *
 * @param {Float32Array} array1 Array to compare
 * @param {Float32Array} array2 Array to compare
 * @param {number} allow_diff Value difference to allow
 * @return {boolean} Equal: true, Otherwise: false
 */
function part_is_equal_f32a(array1, array2, allow_diff) {
  if(array1.length != array2.length) { return false; }

  for(let i = 0; i < array1.length; i++) {
    if(Math.abs(array1[i] - array2[i]) > allow_diff) { return false; }
  }
  return true;
}
