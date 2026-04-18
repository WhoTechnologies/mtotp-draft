Who Technologies
Internet-Draft Intended status: Informational

# MTOTP: Mutual Authentication Extension to TOTP

draft-mtotp-0.1n

## Status of This Memo

This memo provides information for the Internet community. It does not specify an Internet standard of any kind. Distribution of this memo is unlimited.

Portions of this specification are subject to a provisional patent application, pending.

## Copyright Notice

Copyright (C) Who Technologies (2026).

## TODOs

### TODOs Before Sharing Externally

#### Technical Issues

RFC-MTOTP-0.1k > 6 2 Pre-Derivation Hash1
Pre-Derivation Hash was added before we added KDF, and is likely no longer required. Consider removing this step. #technical #external
RFC-MTOTP-0.1k > 7 7 Argon2id Parameters1
VERIFY the math / accuracy of this section #technical #external
RFC-MTOTP-0.1k > 9 Security Considerations1
Security Analysis (at least a minimal one), including what we are protecting against and what we are not (eg: secure transfer of MTOTP messages is on the user). Claude wrote this based on the HOTP security analysis, even through I told it not to. I have not reviewed this and have little interest in reviewing it until the spec is complete (as I told Claude). Leaving it here because maybe it’ll be funny. #technical #external

#### Documentation Issues

- Does this draft really need to be this long? #documentation #external
- Move all design goals, reasoning, background research, etc to Appendix A #external #documentation
- RFC-MTOTP-0.1k > 2 Notation and Terminology2 Update this section (I think we're missing some / maybe remove some...) #documentation #external
- RFC-MTOTP-0.1k > 2 Notation and Terminology2 Add symbols? https://www.ietf.org/rfc/rfc4226.txt #documentation #external
- RFC-MTOTP-0.1k > 3 MTOTP Process Overview1 Rewrite this section #documentation #external
- RFC-MTOTP-0.1k > 3 1 Preparing a MTOTP Message to Send1 Rewrite / more references in this section #documentation #external
- RFC-MTOTP-0.1k > 3 2 Processing a Received MTOTP Message1 Rewrite / more references in this section #documentation #external
- RFC-MTOTP-0.1k > 6 4 Capability Negotiation1 Move Capability Negotiation to the "how to calculate secrets" section. #documentation #external
- RFC-MTOTP-0.1k > 7 KDF Difficulty Scaling1 Split this section into implementation details and documentation / reasoning details, and move the reasoning to the appendix #documentation #external
- RFC-MTOTP-0.1k > 7 4 Cross-Algorithm Equivalence1 Either remove this section or move it to the appendix #documentation #external
- RFC-MTOTP-0.1k > 10 References1 Do we need the references section? have not reviewed. Claude wrote this. Will review once spec complete. #documentation #external
- RFC-MTOTP-0.1k > Appendix A Rationale skip1 Possibly add content here about the reasoning for always exactly filling up the  section 100% (ie: no padding) but may not be necessary as it's briefly covered in the section 5 intro #documentation #external
- RFC-MTOTP-0.1k > Appendix E ABNF Grammar skip1 Decide if needed and if so define formal ABNF per RFC5234 for: #external #documentation

### TODOs Before Publicly Publishing

#### Technical Issues

- RFC-MTOTP-0.1k > 4 1 2 Message Checksum1 Consider whether the checksum length should scale with message length. Longer messages provide more opportunity for transcription error; a longer checksum would provide proportionally stronger error detection at the cost of one bit of IKM entropy per additional checksum bit. #technical #public
- RFC-MTOTP-0.1k > 4 3 3 Compact Format KDF Algorithm1 If removing scrypt as an option, we can remove this bit and apply it to elsewhere (eg: a difficulty level, or a version) instead. #technical #public
- RFC-MTOTP-0.1k > 4 3 4 Compact Format KDF Difficulty2 "fixed to OWASP recommendations" is load-bearing text here — confirm specific parameter values before this document advances. #technical #public
- RFC-MTOTP-0.1k > 4 3 4 Compact Format KDF Difficulty2 consider whether a 1- or 2-bit difficulty hint is feasible within the overhead budget; see TODOs in 4.3.4.1 and 4.3.4.2. #technical #public
- RFC-MTOTP-0.1k > 4 3 4 1 Compact Format scrypt1 Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...? Or remove scrypt completely #technical #public
- RFC-MTOTP-0.1k > 4 3 4 2 Compact Format Argon2id2 Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...? #technical #public
- RFC-MTOTP-0.1k > 4 3 4 2 Compact Format Argon2id2 define the very nebulous concept of "If the specified difficulty level and entropy combined would create a secret too weak to provide proper security, the exchange MUST fail". The biggest risk being PBKDF, which is why it’s banned from compact mode which is designed for smaller amounts of entropy. #technical #public
- RFC-MTOTP-0.1k > 7 KDF Difficulty Scaling1 Rebalance the KDF difficulty scaling based on actual device speeds (potentially use cloud phone rentals, to run tests on actual hardware far beyond what we could find) #technical #public
- RFC-MTOTP-0.1k > 7 3 Baseline Level 01 We almost certainly want to lower the baseline / level 0 requirement to avoid preventing people with older devices from using the protocol. This document was written before we started gathering actual device stats. Once we've completed that, this scale will be updated to match. #technical #public
- RFC-MTOTP-0.1k > 7 5 PBKDF2 Parameters1 Confirm whether a minimum combined IKM entropy level should be required when PBKDF2 is negotiated, and if so what that minimum should be. #technical #public
- RFC-MTOTP-0.1k > 7 6 Scrypt Parameters1 Decide if we keep scrypt, and if not, do we replace it with something beyond argon2id or do we just have two algs? May drop scrypt / and/or add another alg instead. scrypt support was added because I was under the impression that it was fairly universally adapted, however that does not appear to be the case, and if that's accurate, there's no reason to support it. This either saves us a bit in the header, or allows room for another alg. #technical #public
- RFC-MTOTP-0.1k > 7 7 Argon2id Parameters1 Likely want to lower  to 1 to handle devices that cannot parallelize well. #technical #public
- RFC-MTOTP-0.1k > Appendix C Test Vectors skip1 Include test vectors that can be used to verify third party code. Generate and verify all test vectors once parameters are finalized. Authors MUST verify all values; do not use placeholders as reference data. #technical #public
- RFC-MTOTP-0.1k > Appendix D Security Analysis skip1 This appendix requires a dedicated writing session with verified GPU benchmarks. Structure should be comparable to RFC 4226 Appendix A. #technical #public
- RFC-MTOTP-0.1k > Appendix X Reference Implementation skip1 Include a reference implementation that others can test their code against (Appendix X) https://www.ietf.org/rfc/rfc4226.txt / Include a JS? implementation of calculating everything, converting to/from binary, etc. https://www.ietf.org/rfc/rfc4226.txt #technical #public

#### Documentation Issues

- RFC-MTOTP-0.1k > 4 3 4 Compact Format KDF Difficulty1 Add info to Appendix A about this being famous last words all rolled up into one little section right here. 😭 #documentation #public
- RFC-MTOTP-0.1k > 5 MTOTP Message Encodings1 Add that apps MUST/SHOULD encourage the user NOT to share MTOTP messages over insecure channels. Cannot prevent it, but should be warned. #documentation #public
- RFC-MTOTP-0.1k > 7 4 Cross-Algorithm Equivalence1 Recommend that app devs benchmark the device run on first app launch, aiming for ~1-2 second hash time on the device as a maximum. #documentation #public
- RFC-MTOTP-0.1k > 7 6 Scrypt Parameters1 Define memory for each level more precisely so there's no chance of misunderstanding. #documentation #public
- RFC-MTOTP-0.1k > 7 7 Argon2id Parameters1 Define memory for each level more precisely so there's no chance of misunderstanding. #documentation #public

## Abstract

This document describes an extension to the Time-Based One-Time Password (TOTP) algorithm [RFC6238](https://www.rfc-editor.org/info/rfc6238) that enables mutual authentication between two parties.  Standard TOTP provides unidirectional authentication: the verifying party authenticates the code-generating party, but not vice versa.  This document specifies a method by which two parties each contribute Input Keying Material (IKM) to derive two directional TOTP shared secrets, one per direction of verification, without requiring a coordinating server or either party to generate or transmit a complete cryptographic secret.

## Table of Contents

- 1. Introduction
	- 1.1. Scope
	- 1.2. Background
- 2. Notation and Terminology
- 3. MTOTP Process Overview
	- 3.1. Preparing a MTOTP Message to Send
	- 3.2. Processing a Received MTOTP Message
- 4. MTOTP Message Format
	- 4.1. Common Binary Structure
		- 4.1.1. Initial Keying Material (IKM)
		- 4.1.2. Message Checksum
	- 4.2. Extended Format Headers
		- 4.2.1. Extended Format Version Header
		- 4.2.2. Extended v1 Header Structure
		- 4.2.3. Extended v1 KDF Algorithm
		- 4.2.4. Extended v1 KDF Difficulty Scale
	- 4.3. Compact Format Headers
		- 4.3.1. Compact Format Binary Structure
		- 4.3.2. Compact Format Version
		- 4.3.3. Compact Format KDF Algorithm
		- 4.3.4. Compact Format KDF Difficulty
			- 4.3.4.1. Compact Format scrypt
			- 4.3.4.2. Compact Format Argon2id
- 5. MTOTP Message Encodings
	- 5.1. Decimal Encoding
		- 5.1.1. Decimal Encode Procedure
		- 5.1.2. Decimal Decode Procedure
	- 5.2. BIP39 Word List Encoding
		- 5.2.1. BIP39 Encode Procedure
		- 5.2.2. BIP39 Decode Procedure
	- 5.3. Encoded String
		- 5.3.1. Base64URL Encode Procedure
		- 5.3.2. Base64URL Decode Procedure
- 6. Secret Derivation
	- 6.1. IKM Identification
	- 6.2. Pre-Derivation Hash
	- 6.3. Password-Based Key Derivation Function
	- 6.4. Capability Negotiation
	- 6.5. Directional Assignment
	- 6.6. TOTP Application
- 7. KDF Difficulty Scaling
	- 7.1. Attacker Cost Model
	- 7.2. Scale Definition
	- 7.3. Baseline (Level 0)
	- 7.4. Cross-Algorithm Equivalence
	- 7.5. PBKDF2 Parameters
	- 7.6. Scrypt Parameters
	- 7.7. Argon2id Parameters
- 8. Clock Synchronization
- 9. Security Considerations
	- 9.1. MTOTP Message Exchange Channel
	- 9.2. Entropy and Key Strength
	- 9.3. Key Derivation Rationale
	- 9.4. Clock and Replay Considerations
- Appendix A. Rationale
	- A.1. Decimal Encoding and Compact Format
	- A.2. Decimal Encoding: Message Length Derivation
	- A.3. Decimal Encoding: Floating-Point Arithmetic
- Appendix B. Examples
	- B.1. Decimal Encoding: IKM Bit Length Examples
	- B.2. Decimal Encoding: Symbol Count Examples
	- B.3. Decimal Encoding: Message Bit Length Examples

## 1. Introduction

### 1.1. Scope

This document specifies MTOTP, an extension to TOTP [RFC6238](https://www.rfc-editor.org/info/rfc6238) that enables mutual authentication. 

Specifically, this document defines:

- A binary format for MTOTP messages in two versions: a compact version suitable for numerical entry using a fixed KDF Difficulty; and an advanced version carrying explicit negotiated KDF algorithm and parameters;
- Encoding formats for exchanging MTOTP messages over voice, text, and digital channels;
- A key derivation procedure that produces two directional TOTP shared secrets from the IKM values of both parties; and
- Normative TOTP parameters for use with the derived secrets.

Provisioning flows, user interface behavior, contact management, and clock synchronization beyond are outside the scope of this document.

### 1.2. Background

As defined in [RFC6238](https://www.rfc-editor.org/info/rfc6238), TOTP requires a shared secret established at provisioning time.  The verifying party authenticates the code-generating party; the authentication relationship is unidirectional.

Section 9 of [RFC4226](https://www.rfc-editor.org/info/rfc4226) describes a three-pass mutual authentication scheme using HOTP, in which the client presents a first one-time password, the server responds with a second, and the client verifies the server response. The TOTP equivalent requires one party to defer code presentation until the following 30-second time window, a constraint that is impractical for real-time human-to-human interaction.

MTOTP addresses these issues by deriving two directional secrets from a pair of independently generated IKM values, one contributed by each party. The derivation uses the two IKM values in opposite concatenation orderings, such that both devices independently arrive at identical results. Alice’s outbound shared secret equals Bob’s inbound shared secret, and vice versa, without additional coordination after the initial MTOTP message exchange.

In addition, where standard TOTP provisioning relies on the `otpauth://` URI scheme transmitted via QR code or copy-paste, the exchange of the parameters and IKM values can be encoded into a single message that humans can comfortably read, convey, and transcribe. This makes the provisioning exchange viable over voice or other low-bandwidth channels where QR codes and digital copy-paste are unavailable.

## 2. Notation and Terminology

- [ ] Update this section (I think we're missing some / maybe remove some...) #documentation #external

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “NOT RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in RFC2119 when, and only when, they appear in all capitals, as shown here.

The following terms are used throughout this document:

**Input Keying Material (IKM):**
The entropy bits generated by a device and contributed to the shared secret derivation process. The IKM does not include the protocol header or checksum fields of the MTOTP message.

**MTOTP message:**
The binary structure exchanged between two devices during the MTOTP setup procedure.

**$M_{Alice}$ / $M_{Bob}$:**
The MTOTP messages generated by Alice and Bob’s devices.

**$I_{Alice}$ / $I_{Bob}$:**
The IKM fields of $M_{Alice}$ and $M_{Bob}$.

**Alice:**
The local device and its operator. The roles of Alice and Bob are symmetric; each device considers itself Alice and its peer Bob. The labels are used for expository clarity and do not imply initiation order or protocol asymmetry.

**Bob:**
The remote device and its operator.

**Shared Secrets:**
The TOTP keys derived from the combined IKM values of both parties. Two Shared Secrets are produced per MTOTP message exchange, one per direction of verification. Each Shared Secret serves as the key $K$ in the TOTP computation as defined in [RFC4226](https://www.rfc-editor.org/info/rfc4226) and [RFC6238](https://www.rfc-editor.org/info/rfc6238).

**Password-Based Key Derivation Function (KDF):**
A cryptographic function used to derive a Shared Secret from the combined IKM entropy. Referred in this document as just "KDF" to avoid confusion with the PBKDF2 Algorithm.

- [ ] Add symbols? https://www.ietf.org/rfc/rfc4226.txt #documentation #external

## 3. MTOTP Process Overview

The MTOTP overall process includes setting up a pair of shared keys, and then using those shared keys to validate the same person in the future.

Using the shared keys is simply TOTP. The unique MTOTP process is setting up the shared secrets. This involves both Alice and Bob performing two steps:

1. Preparing a MTOTP message to send to the other party (and sending it).
2. Receiving the MTOTP message from the other party (and processing it).

At the completion of those two steps, both parties will have the same shared secrets, and the process continues as a normal TOTP process.

- [ ] Rewrite this section #documentation #external 

### 3.1. Preparing a MTOTP Message to Send

1. Choose an encoding method per [[#5. MTOTP Message Encodings]]. In most cases this also determines your Format (decimal encoding usually uses Compact Format, and everything else uses Extended Format).
2. Calculate the required entropy and generate it (also in MTOTP message encodings).
3. Build the message and encode it.
4. Present the encoded message to Alice for her to (securely) transmit to Bob.

- [ ] Rewrite / more references in this section #documentation #external

### 3.2. Processing a Received MTOTP Message

1. Allow Alice to enter the message received from Bob.
2. Detect the message format, decode it, validate it, and parse the bits.
3. Determine the most preferred common KDF, and the least common KDF Difficulty Level.
4. Run the IKM bits through the selected KDF with parameters specified by the common Difficulty Level.
5. Push the resulting shared secrets into the TOTP algorithm to generate TOTP codes.

- [ ] Rewrite / more references in this section #documentation #external

## 4. MTOTP Message Format

### 4.1. Common Binary Structure

All MTOTP messages share the following invariant structure:

```
MTOTP Message {
  Message Format (1 bit), 
  Format-Specific Headers (..), 
  IKM Bits (..), 
  Message Checksum (5 bits), 
}
```

`..` indicates a variable-length field whose size depends on the Message Format bit and Message Encoding method.

**Message Format (1 bit):**
Determines the structure of the Format-Specific Headers field.

| Value | Meaning                                                         |
| ----- | --------------------------------------------------------------- |
| `0`   | Extended Format. See Section [[#4.2. Extended Format Headers]]. |
| `1`   | Compact Format. See Section [[#4.3. Compact Format Headers]].   |

**Format-Specific Headers (variable):**
Present in all messages.  Structure depends on the value of the Message Format bit. See Sections [[#4.2. Extended Format Headers]] and [[#4.3. Compact Format Headers]].

**IKM Bits (variable):**
Initial Keying Material. See Section [[#4.1.1. Initial Keying Material (IKM)]].

**Message Checksum (5 bits):**
Occupies the five least significant bits of every MTOTP message. See Section [[#4.1.2. Message Checksum]].

#### 4.1.1. Initial Keying Material (IKM)

The IKM field MUST contain a minimum number of bits of entropy generated by a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086). 

IKM length is not a completely free parameter — it is determined by the choice of encoding, message format, and encoding length. The IKM field occupies all remaining bits after the headers and checksum for the message format in use.

Each encoding has a natural granularity: a minimum bit size and step size that the total message length must be a multiple of. For example, BIP39 words each represent 11 bits, so valid message lengths are 11, 22, 33, 44 bits and so on — no intermediate lengths are possible. Once an encoding is chosen, implementations MUST use the maximum IKM length that fits within the encoding's natural granularity, and MUST NOT transmit fewer bits of entropy than the encoding can carry. Doing so would reduce the entropy of the exchange without reducing its size.

Formulas to calculate the encoding granularity for each supported encoding, along with examples, are defined in Section 5.

The minimum combined IKM entropy for an exchange is 64 bits (32 bits per device). Implementations MUST verify the combined IKM length and MUST reject any message that would result in less than 64 bits of combined IKM entropy.

> **Note (Non-Normative):** A minimum combined entropy of 64 bits is intentionally low by cryptographic standards. This reflects a deliberate usability tradeoff for one specific use case of MTOTP: allowing users who are not technically sophisticated to establish a shared secret by exchanging a short numeric string. MTOTP is fully capable of carrying much higher entropy — longer codes, BIP39 words, or Base64URL strings are strongly encouraged where usability permits. The KDF step is specifically chosen and parameterised to harden low-entropy inputs against brute-force attack.

#### 4.1.2. Message Checksum

The five least significant bits of every MTOTP message are the checksum field. This field is computed identically across all message formats, permitting any implementation to validate the checksum prior to decoding the message content.

The checksum additionally serves a limited domain-separation role. Because MTOTP messages carry no dedicated magic number or protocol identifier, the domain-separated HMAC-SHA256 key "MTOTP-v0" makes the checksum distribution distinct from raw SHA-256 output. This reduces — but does not eliminate — the probability that output from an unrelated system is accepted as a valid MTOTP message.

Let B denote the concatenation of all bits preceding the checksum (i.e., including the format bit, all header bits, and the IKM bits), zero-padded on the right to the nearest byte boundary.  The checksum is computed as:

```
checksum_bits = MSB5(HMAC-SHA256("MTOTP-v0", B))
```

where HMAC-SHA256 is as defined in [RFC4231](https://www.rfc-editor.org/info/rfc4231), MSB5(x) denotes the five most significant bits of the first byte of x, and the HMAC key is the ASCII encoding of the literal string "MTOTP-v0".

Implementations MUST verify the checksum upon decoding an MTOTP message and MUST reject any message that fails verification.

- [ ] Consider whether the checksum length should scale with message length. Longer messages provide more opportunity for transcription error; a longer checksum would provide proportionally stronger error detection at the cost of one bit of IKM entropy per additional checksum bit. #technical #public

### 4.2. Extended Format Headers

This format is intended for exchange channels with capacity for additional metadata, such as BIP39 word list, 2D barcode, or encoded string exchange. 

#### 4.2.1. Extended Format Version Header

The first 2 bits of the extended format's headers are a version number that allows future expansion should the need arise. 

```
Extended Format Headers {
  Extended Version (2),
  Version-Specific Headers (..),
}
```

**Extended Version (2 bits):**
Identifies the structure of the Version-Specific Headers field.

| Value | Meaning                                                          |
| ----- | ---------------------------------------------------------------- |
| `01`  | Version 1. See Section [[#4.2.2. Extended v1 Header Structure]]. |
| `10`  | Reserved.                                                        |
| `11`  | Reserved.                                                        |
| `00`  | Reserved.                                                        |

Version numbering begins at `01` rather than `00` so that any valid Extended message is guaranteed to contain a `1` bit within the first three bits, ensuring the binary value is never ambiguous when reconstructed from decimal encoding. See Section [[#5.1. Decimal Encoding]]. Values `00`, `10`, and `11` are reserved for future protocol enhancements or KDF algorithm updates. 

**Version-Specific Headers (variable):**
Structure depends on the Extended Version field.  This document specifies Version 1 only.  See Section [[#4.2.2. Extended v1 Header Structure]].

A receiver that encounters an Extended Version value it does not recognise or support MUST NOT attempt to parse the remainder of the message, MUST reject the message, and MUST inform the user that the peer device uses an unsupported version of the protocol.

#### 4.2.2. Extended v1 Header Structure

```
Version 01 Headers {
  KDF Algorithm (3 bits),
  KDF Difficulty Scale (3 bits),
}
```

**KDF Algorithm (3 bits):**
See Section [[#4.2.3. Extended v1 KDF Algorithm]].

**KDF Difficulty (3 bits):**
See Section [[#4.2.4. Extended v1 KDF Difficulty Scaling]].

**The total message overhead for Extended Format Version 1 is 14 bits:**

| Field            | Bits   |
| ---------------- | ------ |
| Message Format   | 1      |
| Extended Version | 2      |
| KDF Algorithm    | 3      |
| KDF Difficulty   | 3      |
| Message Checksum | 5      |
| **Total**        | **14** |

#### 4.2.3. Extended v1 KDF Algorithm

Each bit in the KDF Algorithm field indicates support for one algorithm. A device MUST set each bit corresponding to an algorithm it supports. More than one bit MAY be set.

| Value | Algorithm                                                              |
| ----- | ---------------------------------------------------------------------- |
| `001` | PBKDF2-HMAC-SHA-256 [RFC8018](https://www.rfc-editor.org/info/rfc8018) |
| `010` | scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914)              |
| `100` | Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106)            |

The negotiated algorithm is the highest-security algorithm for which both devices have set the corresponding bit. The security ordering from lowest to highest is: PBKDF2-HMAC-SHA-256, scrypt, Argon2id.  If no algorithm bit is set in common by both devices, the exchange MUST fail.

- [ ] Consider adding a section for the above paragraph (ie: "how to choose the common kdf algorithm") instead of embedding it in the header description. #documentation 

PBKDF2-HMAC-SHA-256 is included solely for environments with FIPS-140 compliance requirements and is considered the weakest of the three supported algorithms. Implementations SHOULD support at least one of scrypt or Argon2id in addition to PBKDF2, ensuring that PBKDF2 is only negotiated when the peer device supports no stronger algorithm. See [[#7.5. PBKDF2 Parameters]].

#### 4.2.4. Extended v1 KDF Difficulty Scale

The three-bit Difficulty Scaling field encodes an integer value in the range 0–7 (binary `000`–`111`). This value is interpreted as an index into a per-algorithm difficulty parameter table, as specified in Section [[#7. KDF Difficulty Scaling]]. The same index value applies regardless of the negotiated KDF algorithm; the corresponding parameters for the negotiated algorithm are selected from that algorithm's table.

### 4.3. Compact Format Headers

The Compact Format trades configurability for minimal overhead, using fixed KDF Difficulty to preserve as many bits as possible for entropy. It is intended for constrained exchange channels and for users who are uncomfortable with phrase-based entry, preferring to enter a short numeric string on a keypad rather than a word list or encoded string. This is an explicit usability tradeoff: the reduced overhead provides enough security for casual or non-mission-critical use cases, but implementations SHOULD prefer Extended Format where the exchange channel and user comfort permit.

With a 32-bit IKM, the total message length — comprising all header fields, the IKM, and the 5-bit checksum — is 39 bits, giving a maximum decimal value of 2^39 - 1 = 549,755,813,887, which fits within 12 decimal digits.

#### 4.3.1. Compact Format Binary Structure

```
Compact Format Headers {
  KDF Algorithm (1 bit),
}
```

The total message overhead for Compact Format is 7 bits:

| Field            | Bits  |
| ---------------- | ----- |
| Message Format   | 1     |
| KDF Algorithm    | 1     |
| Message Checksum | 5     |
| **Total**        | **7** |

#### 4.3.2. Compact Format Version

The Compact Format contains no version field. Version omission is intentional; the saved bits are allocated to entropy.

#### 4.3.3. Compact Format KDF Algorithm

The Compact Format uses a single bit to indicate the highest-security algorithm the device supports. An implementation MUST support scrypt in order to support Compact Format; scrypt is the baseline and cannot be omitted.

- [ ] If removing scrypt as an option, we can remove this bit and apply it to elsewhere (eg: a difficulty level, or a version) instead. #technical #public 

| Value | scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914) | Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106) |
| ----- | --------------------------------------------------------- | ----------------------------------------------------------- |
| `0`   | Supported                                                 | Not supported                                               |
| `1`   | Supported                                                 | Supported                                                   |

A device that sets this bit to `1` implicitly supports scrypt as a fallback, ensuring that negotiation succeeds with any compliant peer.

PBKDF2-HMAC-SHA-256 is explicitly prohibited in Compact Format. Compact Format provides less entropy than Extended Format by design, and PBKDF2 is insufficiently resistant to brute-force attacks against low-entropy sources. An implementation MUST NOT negotiate PBKDF2 in Compact Format under any circumstances, including interoperability with a peer that does not support scrypt or Argon2id. In such cases, the exchange MUST fail.

#### 4.3.4. Compact Format KDF Difficulty

To conserve space and account for the reduced entropy available in Compact Format, KDF Difficulty is fixed rather than negotiated. Parameters are chosen conservatively, following current OWASP recommendations. 

- [ ] "fixed to OWASP recommendations" is load-bearing text here — confirm specific parameter values before this document advances. #technical #public
- [ ] consider whether a 1- or 2-bit difficulty hint is feasible within the overhead budget; see TODOs in 4.3.4.1 and 4.3.4.2. #technical #public
- [ ] Add info to Appendix A about this being famous last words all rolled up into one little section right here. 😭 #documentation #public

##### 4.3.4.1. Compact Format scrypt

- [ ] Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...? Or remove scrypt completely #technical #public

##### 4.3.4.2. Compact Format Argon2id

- [ ] Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...? #technical #public 
 
If the specified difficulty level and entropy combined would create a secret too weak to provide proper security, the exchange MUST fail. 

- [ ] define the very nebulous concept of "If the specified difficulty level and entropy combined would create a secret too weak to provide proper security, the exchange MUST fail". The biggest risk being PBKDF, which is why it’s banned from compact mode which is designed for smaller amounts of entropy. #technical #public 

## 5. MTOTP Message Encodings

The binary MTOTP message is the normative form; the encodings defined in this section are representations of that binary value that are more easily transmitted by humans.

Each encoding defines a bits-per-symbol value $C$ and a symbol unit (digits, words, or characters). The value of $C$ for each encoding is defined in its respective subsection (Sections [[#5.1. Decimal Encoding]], [[#5.2. BIP39 Word List Encoding]], [[#5.3. Encoded String]]). The formulas below use these values and apply to all encodings.

**IKM Bit Length.** The encoded message must fit exactly into a whole number of symbols, with no partial symbols and no padding. Because the length of the IKM is not transmitted, the decoder re-derives it from $N_S$ — this is only possible if the encoder always fills the encoding completely. Choose a minimum IKM length $B_{min}$ (in bits). The actual IKM length $B_{ikm}$ is the smallest value greater than or equal to $B_{min}$ that satisfies this constraint:

$$B_{ikm} = \left\lfloor \left\lceil (B_{overhead} + B_{min}) \times \frac{1}{C} \right\rceil \times C \right\rfloor - B_{overhead}$$

**Message Bit Length.** On decode, count the number of symbols (digits, words, or characters) received ($N_S$) and calculate the number of bits in the message as:

$$B_{message} = \left\lfloor N_S \times C \right\rfloor$$

For encodings with integer $C$, this is exact. For decimal, where $C=log⁡_{2}(10)$, the floor resolves the fractional remainder.

> See Appendix [[#B.2. Decimal Encoding Symbol Count Examples]] for examples.

Implementations MUST reject and MUST NOT generate any encoding where $B_{min} < 32$ (see Section [[#4.1.1. Initial Keying Material (IKM)]].

- [ ] Add that apps MUST/SHOULD encourage the user NOT to share MTOTP messages over insecure channels. Cannot prevent it, but should be warned. #documentation  #public

### 5.1. Decimal Encoding

Decimal encoding represents an MTOTP message as a string of decimal digits, suitable for voice exchange or manual entry on a numeric keypad. 

> Decimal encoding is designed for use with Compact format (see Appendix [[#A.1. Decimal Encoding and Compact Format]]).

For this encoding, $C = \log_2(10)$.

> See Appendix [[#A.3. Decimal Encoding Floating-Point Arithmetic]] for implementation notes on floating-point evaluation of this value.

Formatting characters such as spaces or hyphens MAY be added for readability and MUST be stripped before decoding. Implementations MUST NOT restrict digit input to a fixed length, and MUST reject input of fewer than 12 digits (which would result in $B_{ikm}<32$). The message length is determined by the digit count after stripping formatting characters, and is validated during decoding per Section [[#4. MTOTP Message Format]].

> See Appendix [[#B.1. Decimal Encoding IKM Bit Length Examples]] for examples.

#### 5.1.1. Decimal Encode Procedure

An implementation SHALL encode an MTOTP binary message to a decimal string as follows:

1. Determine the format (Compact or Extended) and minimum desired IKM entropy $B_{min}$ (in bits).
2. Calculate $B_{ikm}$ per Section [[#5. MTOTP Message Encodings]].
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source [RFC4086].
4. Construct the complete MTOTP binary message per Section [[#4. MTOTP Message Format]].
5. Interpret the binary message as a single non-negative integer in big-endian byte order, where the first byte is the most significant. Within each byte, bit 7 is the most significant bit. Implementations MUST use arbitrary-precision unsigned integer arithmetic and MUST NOT use fixed-width integer types (e.g., uint64) as an intermediate representation, as the message integer may exceed 64 bits.
6. Express the integer as a decimal digit string, left-padded with zeros to exactly $N_S$ digits, where $N_S$ is calculated per Section [[#5. MTOTP Message Encodings]]. The resulting string MUST contain exactly $N_S$ characters, each in the range `0`-`9`. Leading zeros are significant and MUST be preserved; omitting them would alter the binary value they represent.

#### 5.1.2. Decimal Decode Procedure

An implementation SHALL decode an MTOTP decimal string to a binary message as follows:

1. Strip all formatting characters. Any character outside the range `0`-`9` MUST be removed before processing.
2. Count the remaining characters to obtain $N_S$.
3. Calculate $B_{message}$ per Section [[#5. MTOTP Message Encodings]].
4. Parse the digit string as a single non-negative integer using arbitrary-precision unsigned integer arithmetic. Implementations MUST NOT use fixed-width integer types (e.g., uint64) as an intermediate representation.
5. If the parsed integer requires more bits than $B_{message}$ to represent, the message is malformed and the implementation MUST reject it with an error.
6. Serialize the integer to exactly $\lceil B_{message} / 8 \rceil$ bytes in big-endian order, zero-padded on the left. This is the MTOTP binary message.
7. Validate and decode the MTOTP binary message per Section [[#4. MTOTP Message Format]].

> See Appendix [[#A.2. Decimal Encoding Message Length Derivation]] for notes on message length derivation.

### 5.2. BIP39 Word List Encoding

BIP39 word list encoding represents an MTOTP message as a sequence of words drawn from the BIP39 word list [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki), suitable for spoken or text-based exchange.

For this encoding, $C = 11$. Each word in the BIP39 word list corresponds to exactly 11 bits.

Note: This encoding uses the BIP39 word list as an encoding alphabet only. It does not implement the BIP39 standard [BIP39]. In particular, implementations MUST NOT apply or verify a BIP39 checksum; message integrity is provided solely by the MTOTP checksum (Section [[#4.1.2. Message Checksum]]).

#### 5.2.1. BIP39 Encode Procedure

An implementation SHALL encode an MTOTP binary message to a BIP39 word sequence as follows:

1. Determine the format (Compact or Extended) and minimum desired IKM entropy $B_{min}$ (in bits).
2. Calculate $B_{ikm}$ per Section [[#5. MTOTP Message Encodings]].
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source [RFC4086].
4. Construct the complete MTOTP binary message per Section [[#4. MTOTP Message Format]].
5. Read the message bits from most significant to least significant, taking 11 bits at a time.
6. For each 11-bit group, interpret it as an unsigned integer in the range 0–2047 and select the corresponding entry from the BIP39 word list.

#### 5.2.2. BIP39 Decode Procedure

An implementation SHALL decode a BIP39 word sequence to an MTOTP binary message as follows:

1. For each word in the input sequence, locate its index in the BIP39 word list. If any word is not found, the message is malformed and the implementation MUST reject it.
2. Concatenate the 11-bit binary representations of the word indices, from first word to last. This is the MTOTP binary message.
3. Validate and decode the MTOTP binary message per Section 4.

### 5.3. Encoded String

Encoded string format represents an MTOTP message as a Base64URL-encoded string [RFC4648], suitable for copy-paste over digital channels and for use as a URI or app intent.

For this encoding, $C = 6$.

Format:
```
MTOTP;base64url,<data>
```

`<data>` is the MTOTP binary message encoded as Base64URL per [RFC4648] Section [[#5. MTOTP Message Encodings]]. The prefix `MTOTP;base64url,` is case-sensitive. Decoders MUST reject strings that do not conform to this format.

#### 5.3.1. Base64URL Encode Procedure

An implementation SHALL encode an MTOTP binary message to a Base64URL string as follows:

1. Determine the format (Compact or Extended) and minimum desired IKM entropy $B_{min}$ (in bits).
2. Calculate $B_{ikm}$ per Section [[#5. MTOTP Message Encodings]].
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source [RFC4086].
4. Construct the complete MTOTP binary message per Section [[#4. MTOTP Message Format]].
5. Encode the binary message as Base64URL per [RFC4648] §5 (URL and Filename Safe Alphabet).
6. Prepend the ASCII prefix `MTOTP;base64url,` to produce the encoded string.

An encoded string MAY be represented as a QR code using any conformant QR code encoder for in-person or camera-based exchange. No additional specification is required for QR encoding.

#### 5.3.2. Base64URL Decode Procedure

An implementation SHALL decode a Base64URL encoded string to an MTOTP binary message as follows:

1. Verify the string begins with the ASCII prefix `MTOTP;base64url,`. If not, the message is malformed and the implementation MUST reject it with an error.
2. Strip the prefix to obtain the Base64URL encoded data.
3. Decode the Base64URL data per [RFC4648] §5 (URL and Filename Safe Alphabet). The resulting bit string is the MTOTP binary message.
4. Validate and decode the MTOTP binary message per Section [[#4. MTOTP Message Format]].

## 6. Secret Derivation

### 6.1. IKM Identification

Both MTOTP messages MUST be exchanged and decoded per Section [[#5. MTOTP Message Encodings]] before derivation begins. The IKM field of each decoded message is identified per the binary structure defined in Section [[#4.1. Common Binary Structure]].

Let:
IKM_Alice = the IKM field of M_Alice
IKM_Bob   = the IKM field of M_Bob

Only the IKM fields are used as inputs to the derivation.  The header and checksum fields do not contribute to the entropy of the derived secrets.

### 6.2. Pre-Derivation Hash

Two 256-bit intermediate values are computed by applying SHA-256 to the IKM fields concatenated in opposite orderings:

```
  H_out = SHA-256(IKM_Alice || IKM_Bob)
  H_in  = SHA-256(IKM_Bob   || IKM_Alice)
```

The pre-derivation hash applies SHA-256 to both orderings of the IKM fields. This ensures that even low-entropy IKM values are distributed across the full 256-bit output space, increasing the cost of precomputation attacks. It does not increase the entropy of the IKM inputs.

- [ ] Pre-Derivation Hash was added before we added KDF, and is likely no longer required. Consider removing this step. #technical #external 

### 6.3. Password-Based Key Derivation Function

The KDF algorithm and parameters are determined by the message format, as follows.

The protocol salt `MTOTP-v0` is a fixed ASCII string used by all KDF invocations in both formats.  It is not secret and does not contribute entropy.  It provides domain separation from other uses of the same KDF functions and distinguishes this protocol version from future revisions.

**Note:** RFC 9106 recommends a randomly generated 128-bit salt for Argon2id. MTOTP uses a fixed protocol salt instead. This forces an attacker to build a precomputation table specifically for this protocol rather than reusing existing tables. Per-exchange uniqueness is provided by the IKM entropy.

Two Shared Secrets are derived:

```
  SharedSecret_out = KDF(H_out, salt="MTOTP-v0", <parameters>)
  SharedSecret_in  = KDF(H_in,  salt="MTOTP-v0", <parameters>)
```

KDF computation occurs once per contact establishment, not per authentication event.

### 6.4. Capability Negotiation

- [ ] Move Capability Negotiation to the "how to calculate secrets" section. #documentation #external

Each party advertises:

- A bitmask of supported algorithms (3 bits: Argon2id, scrypt, PBKDF2)
- A single maximum supported difficulty level (3 bits: 0-7)

Negotiation selects:

1. The strongest algorithm supported by both parties, in preference
   order Argon2id > scrypt > PBKDF2.
2. The minimum of the two advertised maximum levels, evaluated against
   the selected algorithm.

If PBKDF2 is selected and the shared entropy is below the PBKDF2
minimum specified in Section N.7, pairing MUST fail.

### 6.5. Directional Assignment

From Alice’s perspective, the derived secrets are assigned as follows:

```
SharedSecret_out:  Alice uses this secret as TOTP key K to generate codes she presents to Bob.

SharedSecret_in:   Alice uses this secret as TOTP key K to verify codes that Bob presents to her.
```

The same calculation is performed by both parties. When Bob derives his keys, he simply swaps the labels — his own IKM is $KM_{Alice}$ and Alice's IKM is $IKM_{Bob}$​. The result is that both parties independently arrive at matching directional keys without any additional coordination.

### 6.6. TOTP Application

Each Shared Secret is used independently as the key K in TOTP [RFC6238](https://www.rfc-editor.org/info/rfc6238):

```
TOTP(K, T) = HOTP(K, T)
```

where T is the time step counter as defined in [RFC6238](https://www.rfc-editor.org/info/rfc6238).  The following parameters apply to both derived secrets and are fixed by this specification:

```
Hash algorithm:  HMAC-SHA-256 [RFC2104](https://www.rfc-editor.org/info/rfc2104)
Time step (X):   30 seconds
T0:              Unix epoch (January 1, 1970, 00:00:00 UTC)
Output digits:   6
```

These parameters were chosen for compatibility with widely deployed TOTP implementations. Fixing them eliminates the need for per-exchange parameter negotiation and removes them from the message format overhead.

These parameters are not subject to negotiation.  Both parties MUST use these parameters.

Implementations MUST comply with [RFC6238](https://www.rfc-editor.org/info/rfc6238) for all TOTP computation, including time step calculation, dynamic truncation, and output formatting.

## 7. KDF Difficulty Scaling

- [ ] Split this section into implementation details and documentation / reasoning details, and move the reasoning to the appendix #documentation #external 
- [ ] Rebalance the KDF difficulty scaling based on actual device speeds (potentially use cloud phone rentals, to run tests on actual hardware far beyond what we could find) #technical #public

The KDF difficulty field provides forward-compatible tuning of key-derivation work within a single protocol version, without consuming additional header bits as hardware improves. It is constrained by the following goals:

1. A single integer expresses difficulty for all supported KDFs.
2. The same integer value across algorithms represents approximately equivalent attacker cost, such that capability advertisement does not need to be per-algorithm.
3. The scale spans from parameters implementable on commodity mobile hardware (2018-era smartphones) through parameters intended for hardware at least one decade beyond publication.
4. Parameters for every level are fully specified in this document; no runtime parameter derivation is performed. Both parties MUST produce identical parameters from identical inputs.

### 7.1. Attacker Cost Model

Security is measured in **time-area product (AT)**, the product of the circuit area occupied by a single KDF evaluation and the wall-clock time required for that evaluation on attacker hardware [ARGON2-PAPER].  This is the metric Argon2 was explicitly designed to maximize, and it is the metric used in this document to compare levels across algorithms.

The protocol permits a minimum of 64 bits of shared entropy and does not use a salt. The attacker is therefore assumed to perform keyspace precomputation amortized across all users sharing a given entropy length. A difficulty level MUST be chosen such that the AT cost of computing $2^{64}$ KDF evaluations exceeds any economically rational adversary's budget.

### 7.2. Scale Definition

The difficulty field is 3 bits, yielding 8 levels (0 through 7). Each increment of the difficulty field represents approximately a 4x increase in attacker AT cost.  The 4x step was chosen for the following reasons:

1. **It matches scrypt's natural granularity.** scrypt's cost parameter N MUST be a power of 2 [RFC7914].  Each doubling of N doubles both memory and the number of sequential operations over that memory, yielding 4x AT cost per step.  Finer-grained scrypt scaling requires manipulating the r parameter, which departs from the widely-deployed $r=8$
   configuration recommended by [RFC7914] and degrades performance on common implementations due to cache effects.
2. **It aligns with the hardware improvement rate.**  Moore's Law doubles transistor density roughly every 18-24 months. A 4x cost step therefore corresponds to approximately 3-4 years of attacker hardware improvement. An 8-level scale thus covers 24-32 years of projected
   hardware advancement, which allows additional leeway for unforeseen advancement during that period.
3. **It respects the precision of the underlying threat model.** Estimates of future attacker capability (GPU memory bandwidth, ASIC economics, TMTO advances) are uncertain to well more than a factor of 2.

### 7.3. Baseline (Level 0)

- [ ] We almost certainly want to lower the baseline / level 0 requirement to avoid preventing people with older devices from using the protocol. This document was written before we started gathering actual device stats. Once we've completed that, this scale will be updated to match. #technical #public

Level 0 is calibrated to approximately 3-4x the AT cost of the OWASP 2024 minimum recommendations for Argon2id and scrypt [OWASP-PSCS].  The OWASP minimums are chosen for server-side password verification, where the server processes many concurrent authentications per second and must minimize per-request wall time. This protocol performs KDF evaluation once per pairing (not per authentication code), so a larger per-evaluation cost is acceptable.

Level 0 targets approximately 1 second of wall-clock time on a 2018-era budget smartphone (Cortex-A53-class SoC, LPDDR3/LPDDR4 memory). Implementations running on faster hardware will complete level 0 in proportionally less time.

### 7.4. Cross-Algorithm Equivalence

- [ ] Either remove this section or move it to the appendix #documentation #external

The scale is designed such that the same numeric level across algorithms produces approximately equivalent attacker AT cost.  Equivalence is approximate rather than exact because:

1. The underlying compression functions differ (BLAKE2b for Argon2id, Salsa20/8 for scrypt, HMAC-SHA256 for PBKDF2) and have different constant-factor costs per operation on both defender and attacker hardware.
2. TMTO resistance differs between algorithms.  The nominal AT cost figures above do not account for the ~1.33x reduction achievable against Argon2id [RFC9106] or the larger reductions achievable against scrypt.
3. PBKDF2 is not memory-hard and provides no ASIC resistance. PBKDF2 level N provides far less effective security than scrypt or Argon2id level N against a well-resourced attacker.

Capability advertisement during pairing specifies a single maximum level applicable to all supported algorithms.  Implementations SHOULD benchmark on first run and set this level to the highest at which every supported algorithm completes within the implementation's time budget.

- [ ] Recommend that app devs benchmark the device run on first app launch, aiming for ~1-2 second hash time on the device as a maximum. #documentation #public

### 7.5. PBKDF2 Parameters

PBKDF2 [RFC8018] is included solely to satisfy regulatory requirements that mandate FIPS 140-validated KDFs.  Because PBKDF2-HMAC-SHA256 is not memory-hard and is efficiently attacked by commodity GPUs, this protocol imposes a minimum shared entropy of [TBD: 80] bits when PBKDF2 is negotiated. 64-bit shared entropy MUST NOT be used with PBKDF2.

PBKDF2 iteration counts per level (HMAC-SHA256 PRF):

| Level | Iterations     | Ratio to OWASP 2024 minimum |
|-------|----------------|-----------------------------|
| 0     | 1,000,000      | ~1.7x                       |
| 1     | 4,000,000      | ~6.7x                       |
| 2     | 16,000,000     | ~27x                        |
| 3     | 64,000,000     | ~107x                       |
| 4     | 256,000,000    | ~427x                       |
| 5     | 1,024,000,000  | ~1707x                      |
| 6     | 4,096,000,000  | ~6827x                      |
| 7     | 16,384,000,000 | ~27307x                     |

Level 0 exceeds the [OWASP-PSCS] current recommendation of 600,000 iterations for HMAC-SHA256.  The historical OWASP trajectory for PBKDF2-HMAC-SHA256 is approximately:

| Year  | Recommended iterations |
| ----- | ---------------------- |
| 2000  | 1,000 ([RFC2898])      |
| 2010  | 10,000                 |
| 2021  | 310,000 ([OWASP-PSCS]) |
| 2023+ | 600,000 ([OWASP-PSCS]) |

This represents a ~600x increase over approximately 23 years, or approximately 10 bits of work.  The 4x per-level schedule provides comparable headroom within levels 0-7.

- [ ] Confirm whether a minimum combined IKM entropy level should be required when PBKDF2 is negotiated, and if so what that minimum should be. #technical #public
- [ ] 

### 7.6. Scrypt Parameters

- [ ] Decide if we keep scrypt, and if not, do we replace it with something beyond argon2id or do we just have two algs? May drop scrypt / and/or add another alg instead. scrypt support was added because I was under the impression that it was fairly universally adapted, however that does not appear to be the case, and if that's accurate, there's no reason to support it. This either saves us a bit in the header, or allows room for another alg. #technical #public

Parameters: $N$ = cost parameter (power of 2 per [RFC7914]), $r = 8$, $p = 1$. The $r=8$, $p=1$ configuration is explicitly recommended in [RFC7914] Section 2 and is the configuration under which scrypt's memory-hardness proofs in [ALWEN-SCRYPT-2016] apply.

| Level | $log_{2}(N)$ | Memory ($128 \times N \times r$ bytes) | AT cost (relative to L0) |
| ----- | ------------ | -------------------------------------- | ------------------------ |
| 0     | 15           | 32 MiB                                 | 1x                       |
| 1     | 16           | 64 MiB                                 | 4x                       |
| 2     | 17           | 128 MiB                                | 16x                      |
| 3     | 18           | 256 MiB                                | 64x                      |
| 4     | 19           | 512 MiB                                | 256x                     |
| 5     | 20           | 1 GiB                                  | 1024x                    |
| 6     | 21           | 2 GiB                                  | 4096x                    |
| 7     | 22           | 4 GiB                                  | 16384x                   |

- [ ] Define memory for each level more precisely so there's no chance of misunderstanding. #documentation #public

scrypt's AT cost scales as $N^2$ because each increment of $log_{2}(N)$ doubles both the memory block count and the number of sequential operations over that memory.  Each level therefore corresponds to a single $+1$ step in $log_{2}(N)$, matching the 4x per-level AT target naturally.

Level 0 matches the current OWASP recommended minimum of $N=2^17$, $r=8$, $p=1$ [OWASP-PSCS] scaled down by one $log_{2}(N)$ step.  Level 2 matches the OWASP minimum directly.

**TMTO Note**

scrypt has been proven maximally memory-hard in the parallel random oracle model [ALWEN-SCRYPT-2016].  However, scrypt is susceptible to certain time-memory tradeoffs not present in Argon2id; specifically, the [ARGON2-PAPER] introduction notes that "the existence of a trivial time-memory tradeoff" in scrypt motivated the development of Argon2. At equivalent nominal AT parameters, Argon2id provides stronger effective resistance to ASIC-based attackers.  For this reason, Argon2id is the preferred algorithm in negotiation; scrypt is retained for implementations that lack a well-optimized Argon2 library.

### 7.7. Argon2id Parameters

- [ ] Likely want to lower $p$ to 1 to handle devices that cannot parallelize well. #technical #public

Parameters: $m$ = memory in KiB, $t$ = iterations, $p$ = lanes (per [RFC9106] guidance).  Variant is Argon2id (hybrid), version 0x13.

| Level | $m$ (MiB) | $t$ | $p$ | AT cost (relative to L0) |
| ----- | --------- | --- | --- | ------------------------ |
| 0     | 64        | 2   | 4   | 1x                       |
| 1     | 128       | 4   | 4   | 4x                       |
| 2     | 256       | 8   | 4   | 16x                      |
| 3     | 512       | 16  | 4   | 64x                      |
| 4     | 1024      | 32  | 4   | 256x                     |
| 5     | 2048      | 64  | 4   | 1024x                    |
| 6     | 4096      | 128 | 4   | 4096x                    |
| 7     | 8192      | 256 | 4   | 16384x                   |

- [ ] Define memory for each level more precisely so there's no chance of misunderstanding. #documentation #public

Level 0 matches the [RFC9106] SECOND RECOMMENDED option for memory-constrained environments ($m$=64 MiB, $t$=3, $p$=4), with $t$ reduced to $2$ to bring per-evaluation time closer to 1 second on low-end mobile hardware. Level 2 approximates the [RFC9106] FIRST RECOMMENDED option ($m$=2 GiB, $t$=1) in AT cost terms, and level 5 exceeds it by a factor of approximately 64.

**TMTO Resistance**

Argon2id provides strong resistance to time-memory tradeoff (TMTO) attacks. Per [RFC9106] Section 7.2, the best known attack on t-pass Argon2id is the ranking tradeoff attack, reducing the AT product by a factor of 1.33 for $t >= 2$.  At $t=2$ and above, further increases in $t$ do not meaningfully improve TMTO resistance for this range of memory sizes.

However, increasing $t$ beyond 2 remains useful in this protocol because it proportionally increases the attacker's compute requirements at fixed memory. The AT cost scales linearly in $t$ regardless of TMTO resistance. Doubling $t$ per level therefore doubles attacker work independent of memory considerations.

Per [RFC9106], to completely prevent [AB16] time-space tradeoffs, the number of passes MUST exceed $log_{2}($memory_in_blocks$) - 26$.  At $m$=8192 MiB (level 7), this requires $t >= log_{2}(8388608) - 26 = 23 - 26 = -3$, which is trivially satisfied.  At all levels in this table, the [AB16] tradeoff is fully prevented.

- [ ] VERIFY the math / accuracy of this section #technical #external

## 8. Clock Synchronization

Correct TOTP operation requires that both devices maintain accurate Unix time.  Implementations SHOULD follow the clock synchronization and resynchronization guidance in [RFC6238](https://www.rfc-editor.org/info/rfc6238), including acceptance of codes from adjacent time steps.

## 9. Security Considerations

- [ ] Security Analysis (at least a minimal one), including what we are protecting against and what we are not (eg: secure transfer of MTOTP messages is on the user). Claude wrote this based on the HOTP security analysis, even through I told it not to. I have not reviewed this and have little interest in reviewing it until the spec is complete (as I told Claude). Leaving it here because maybe it’ll be funny. #technical #external

### 9.1. MTOTP Message Exchange Channel

The security of MTOTP depends on the confidentiality of the MTOTP message exchange.  An adversary who obtains both M_Alice and M_Bob can derive both Shared Secrets and impersonate either party.

Implementations SHOULD instruct users to exchange MTOTP messages only over channels where third-party interception is unlikely, such as a direct voice call, in-person exchange, or an end-to-end encrypted channel.  The HOTP specification [RFC4226](https://www.rfc-editor.org/info/rfc4226) requires OTP values to be transmitted over secure channels such as TLS or IPsec; MTOTP cannot mandate a channel type for MTOTP message exchange, as this exchange is out-of-band and under user control.

An active adversary substituting both MTOTP messages must have control of the exchange channel at the time of exchange.  Voice channels where speakers authenticate each other by voice recognition reduce the practical feasibility of this attack.

### 9.2. Entropy and Key Strength

The combined entropy available to the derived Shared Secrets is bounded by the sum of the entropies of IKM_Alice and IKM_Bob. For compact format messages with a 32-bit IKM, the combined entropy is 64 bits.

Implementations MUST use a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086) to generate IKM values.  A low-entropy contribution from either party reduces the security of both Shared Secrets .

Implementations SHOULD inform users when the combined entropy level of their exchange may be insufficient for high-security applications.

### 9.3. Key Derivation Rationale

The KDF options in both message versions reflect resistance to GPU and ASIC-accelerated brute-force attacks, adjusted for time-memory tradeoff (TMTO) cost.

scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914) is memory-hard, which limits GPU parallelism. However, scrypt is subject to a TMTO vulnerability in which an attacker using reduced memory incurs only a sub-linear time penalty.  See [[#Appendix D. Security Analysis skip]].

Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106) provides improved TMTO resistance over scrypt. Its data-dependent memory access pattern requires super-linear additional computation when memory is reduced, and inter-lane dependencies prevent independent parallel attacks.  See Appendix B.

Compact format fixed parameters are selected to meet or exceed the OWASP minimum configurations [OWASP] for each algorithm, while
remaining practical on memory-constrained mobile platforms. Extended format permits explicit parameter selection across the full range of configurations recommended by [RFC9106](https://www.rfc-editor.org/info/rfc9106) and [OWASP], including values appropriate for server and desktop deployments.

The SHA-256 pre-derivation step ([[#5.2. Pre-Derivation Hash]]) and the fixed protocol salt “MTOTP-v0” ([[#5.3. Password-Based Key Derivation Function]]) provide domain separation. Neither increases the entropy of the IKM inputs.

### 9.4. Clock and Replay Considerations

TOTP codes are valid only within the time step in which they are generated.  Implementations SHOULD follow the replay prevention guidance of [RFC6238](https://www.rfc-editor.org/info/rfc6238), including rejection of previously accepted OTP values within the current time step.

## Appendix A. Rationale

- [ ] Possibly add content here about the reasoning for always exactly filling up the $B_{ikm}$ section 100% (ie: no padding) but may not be necessary as it's briefly covered in the section 5 intro #documentation #external

### A.1. Decimal Encoding and Compact Format

Compact format was designed specifically for use with decimal encoding. The goal was to allow two parties to establish mutual authentication by exchanging a short numeric code — something a person can read aloud, hear, and enter on a keypad without difficulty.

To maximize entropy within a small number of digits, Compact format minimizes header overhead, leaving as many bits as possible for IKM.

Voice channels (telephone, video call) are a natural fit for this exchange: they are widely accessible, require no special software, and do not leave a long-lived record of the exchanged message. Transmitting an MTOTP message over a persistent unencrypted channel such as email is discouraged (see Section X).

Decimal encoding is not the highest-entropy encoding available, and Compact format carries fewer negotiation options than Extended. These are accepted tradeoffs in exchange for simplicity and accessibility.

### A.2. Decimal Encoding: Message Length Derivation

The bit length of a decimal-encoded message is fully determined by the digit count. No out-of-band length field is required. Both Compact (Format bit `0`) and Extended (Format bit `1`) messages are recovered correctly because $B_{message}$ is derived from $N_S$ independently of the integer's magnitude.

### A.3. Decimal Encoding: Floating-Point Arithmetic

The IKM bit length and message bit length formulas for decimal encoding require floating-point evaluation of $\log_{10}(2)$ and $\log_2(10)$. This has been verified to produce correct results for all values within the scope of this specification using IEEE 754 double-precision arithmetic. Implementations
SHOULD verify their computed values against the test vectors in Appendix B, which serve as the authoritative reference regardless of floating-point implementation.

## Appendix B. Examples

### B.1. Decimal Encoding: IKM Bit Length Examples

The following table illustrates the chunking effect of the IKM bit length formula (Section [[#5. MTOTP Message Encodings]]) for decimal encoding with Compact format overhead ($B_{overhead} = 7$).

| $B_{overhead}$ | $B_{min}$ | Calculated $B_{ikm}$ |
| -------------- | --------- | -------------------- |
| 7              | 32        | 32                   |
| 7              | 33        | 36                   |
| 7              | 34        | 36                   |
| 7              | 35        | 36                   |
| 7              | 36        | 36                   |
| 7              | 37        | 39                   |
| 7              | 38        | 39                   |
| 7              | 39        | 39                   |
| 7              | 40        | 42                   |
| ...etc         |           |                      |

### B.2. Decimal Encoding: Symbol Count Examples

The following table illustrates calculated digit counts for Compact format ($B_{overhead} = 7$).

| $B_{overhead}$ | $B_{ikm}$ | $B_{overhead}+B_{ikm}$ | Calculated $N_S$ |
| -------------- | --------- | ---------------------- | ---------------- |
| 7              | 32        | 39                     | 12               |
| 7              | 36        | 43                     | 13               |
| 7              | 39        | 46                     | 14               |
| 7              | 42        | 49                     | 15               |
| ...etc         |           |                        |                  |

### B.3. Decimal Encoding: Message Bit Length Examples

The following table illustrates calculated message bit lengths for Compact format ($B_{overhead} = 7$).

| $N_S$  | Calculated $B_{message}$ |
| ------ | ------------------------ |
| 12     | 39                       |
| 13     | 43                       |
| 14     | 46                       |
| 15     | 49                       |
| ...etc |                          |
