/**
 * @file Encoding/decoding functions for `volume_modify` packet
 *
 * More detail of packet protocol, see `packet-protocol.md`
 *
 * @author aKuad
 */

/**
 * Packet type ID of volume modify packet
 */
export const VOLUME_MODIFY_PACKET_TYPE_ID = 0x20;


/**
 * Create volume_modify packet
 *
 * @param {number} lane_id Lane ID to control
 * @param {number} modified_volume Modified volume value
 * @returns {Uint8Array} Encoded packet
 *
 * @throws {TypeError} If `lane_id` is not `number`
 * @throws {TypeError} If `modified_volume` is not `number`
 * @throws {RangeError} If `lane_id` is not in 0~255
 * @throws {RangeError} If `modified_volume` is not in 0~255
 */
export function packet_volume_modify_encode(lane_id, modified_volume) {
  // Arguments type checking
  if(typeof lane_id !== "number") {
    throw new TypeError("lane_id must be number");
  }
  if(typeof modified_volume !== "number") {
    throw new TypeError("modified_volume must be number");
  }

  // Arguments range checking
  if(lane_id < 0 || lane_id > 255) {
    throw new RangeError("lane_id must be in 0~255");
  }
  if(modified_volume < 0 || modified_volume > 255) {
    throw new RangeError("modified_volume must be in 0~255");
  }

  return Uint8Array.of(VOLUME_MODIFY_PACKET_TYPE_ID, lane_id, modified_volume);
}


/**
 * Unpack volume_modify packet
 *
 * @param {Uint8Array} raw_packet Encoded packet
 * @returns {Array<number>} Decoded data - Lane ID and modified volume
 *
 * @throws {TypeError} If `raw_packet` is not `Uint8Array`
 * @throws {RangeError} If `raw_packet` is an empty array
 * @throws {RangeError} If `raw_packet` type ID is not volume_modify packet ID
 * @throws {RangeError} If `raw_packet` length is not 3
 */
export function packet_volume_modify_decode(raw_packet) {
  // Packet type verification
  if(!is_volume_modify_packet(raw_packet)) {
    throw new RangeError("Invalid packet, it is not an volume_modify packet");
  }

  // Arguments range checking
  if(raw_packet.length !== 3) {
    throw new RangeError("Invalid packet, length must be 3");
  }

  return [raw_packet[1], raw_packet[2]];
}


/**
 * Verify the packet is volume_modify packet
 *
 * Note: It verify only type and packet ID. Packet structure will not be verified.
 *
 * @param {Uint8Array} raw_packet Packet to verify
 * @returns {boolean} It is a volume_modify packet: true, otherwise: false
 *
 * @throws {TypeError} If `raw_packet` is not `Uint8Array`
 * @throws {RangeError} If `raw_packet` is an empty array
 */
export function is_volume_modify_packet(raw_packet, throw_on_invalid = false) {
  try {
    // Arguments type checking
    if(!(raw_packet instanceof Uint8Array)) {
      throw new TypeError("raw_packet must be Uint8Array");
    }

    // Packet content availability checking
    if(raw_packet.length === 0) {
      throw new RangeError("Empty array passed");
    }

    if(raw_packet[0] !== VOLUME_MODIFY_PACKET_TYPE_ID) {
      throw new RangeError("It is not a volume_modify packet");
    }

    if(raw_packet.length < 3) {
      throw new RangeError("Too short bytes as volume modify packet");
    }
    if(raw_packet.length > 3) {
      throw new RangeError("Too long bytes as volume modify packet");
    }
  } catch(e) {
    if(throw_on_invalid) {
      throw e;
    } else {
      return false;
    }
  }

  return true;
}
