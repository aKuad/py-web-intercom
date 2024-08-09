/**
 * @file Tests for `packet_conv/volume_modify.js`
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

import { packet_volume_modify_encode, packet_volume_modify_decode, is_volume_modify_packet } from "../../../static/packet_conv/volume_modify.js"
import { describe, test, expect } from "vitest"


describe("true_cases", () => {
  test("enc_dec_verify", () => {
    const lane_id_org = 1;
    const modified_volume_org = 100;
    const raw_packet = packet_volume_modify_encode(lane_id_org, modified_volume_org);
    const [lane_id_prc, modified_volume_prc] = packet_volume_modify_decode(raw_packet);

    expect(is_volume_modify_packet(raw_packet)).toBe(true);
    expect(lane_id_prc).toBe(lane_id_org);
    expect(modified_volume_prc).toBe(modified_volume_org);
  });


  test("verify_ng", () => {
    const lane_id_org = 1;
    const modified_volume_org = 100;
    const raw_packet_correct = packet_volume_modify_encode(lane_id_org, modified_volume_org);

    const raw_packet_invalid_empty     = new Uint8Array();
    const raw_packet_invalid_id        = Uint8Array.of(0x30, ...raw_packet_correct.slice(1));  // as non 0x20 byte
    const raw_packet_invalid_too_short = raw_packet_correct.slice(0, -1);
    const raw_packet_invalid_too_long  = Uint8Array.of(...raw_packet_correct, 0); // 0 as an over length byte

    expect(is_volume_modify_packet("")                          ).toBe(false);  // string "" as non Uint8Array
    expect(is_volume_modify_packet(raw_packet_invalid_empty)    ).toBe(false);
    expect(is_volume_modify_packet(raw_packet_invalid_id)       ).toBe(false);
    expect(is_volume_modify_packet(raw_packet_invalid_too_short)).toBe(false);
    expect(is_volume_modify_packet(raw_packet_invalid_too_long) ).toBe(false);

    expect(() => is_volume_modify_packet(""                          , true)).toThrowError(new TypeError ("raw_packet must be Uint8Array"));
    expect(() => is_volume_modify_packet(raw_packet_invalid_empty    , true)).toThrowError(new RangeError("Empty array passed"));
    expect(() => is_volume_modify_packet(raw_packet_invalid_id       , true)).toThrowError(new RangeError("It is not a volume_modify packet"));
    expect(() => is_volume_modify_packet(raw_packet_invalid_too_short, true)).toThrowError(new RangeError("Too short bytes as volume modify packet"));
    expect(() => is_volume_modify_packet(raw_packet_invalid_too_long , true)).toThrowError(new RangeError("Too long bytes as volume modify packet"));
  });
});


describe("err_cases", () => {
  test("enc_invalid_type", () => {
    const lane_id = 1;
    const modified_volume = 100;

    expect(() => packet_volume_modify_encode("", modified_volume)).toThrowError(new TypeError("lane_id must be number"));
    expect(() => packet_volume_modify_encode(lane_id, ""        )).toThrowError(new TypeError("modified_volume must be number"));
  });


  test("enc_invalid_value", () => {
    const lane_id = 1;
    const modified_volume = 100;

    expect(() => packet_volume_modify_encode(256, modified_volume)).toThrowError(new RangeError("lane_id must be in 0~255"));
    expect(() => packet_volume_modify_encode(-1 , modified_volume)).toThrowError(new RangeError("lane_id must be in 0~255"));
    expect(() => packet_volume_modify_encode(lane_id, 256        )).toThrowError(new RangeError("modified_volume must be in 0~255"));
    expect(() => packet_volume_modify_encode(lane_id, -1         )).toThrowError(new RangeError("modified_volume must be in 0~255"));
  });


  // test("dec_invalid_type", () => {
  //   // packet verification integrated to `is_volume_modify_packet` tests
  // });

  // test("dec_invalid_value", () => {
  //   // packet verification integrated to `is_volume_modify_packet` tests
  // });

  // test("verify_invalid_type", () => {
  //   // no error cases of `is_volume_modify_packet`
  // });

  // test("verify_invalid_value", () => {
  //   // no error cases of `is_volume_modify_packet`
  // });
});
