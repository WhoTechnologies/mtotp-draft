Who Technologies
Internet-Draft Intended status: Informational

# MTOTP: Mutual Authentication Extension to TOTP

draft-mtotp-0.1p

## Status of This Memo

This memo provides information for the Internet community. It does not specify an Internet standard of any kind. Distribution of this memo is unlimited.

Portions of this specification are subject to a provisional patent application, pending.

## Copyright Notice

Copyright © Who Technologies (2026).

## Abstract

This document describes an extension to the Time-Based One-Time Password (TOTP) algorithm {{!RFC6238}} that enables mutual authentication between two parties.  Standard TOTP provides unidirectional authentication: the verifying party authenticates the code-generating party, but not vice versa.  This document specifies a method by which two parties each contribute Input Keying Material (IKM) to derive two directional TOTP shared secrets, one per direction of verification, without requiring a coordinating server or either party to generate or transmit a complete cryptographic secret.

## Critical Review Notice

> [!NOTE]
> **This document is a work in progress, and some critical context is currently missing. This section exists to provide that context until the appropriate text is added to the sections below.**
> 
> **Scope:**<br />
> This protocol focussed on setting up a pair of TOTP secrets, in a way that allows humans to perform the exchange offline. All the same TOTP "vulnerabilities" (i.e.: intercepting shares secrets during initialization) apply to this protocol as well. We encourage the operators to share their messages over a secure connection, in the same way that TOTP recommends sharing the secret over a TLS connection, however Mallory listening in on that initialization session is outside the scope of this document (just like spying on the initial TOTP QR code is outside TOTP's scope).
> 
> **Entropy:**<br />
> 64 bits of entropy is VERY LOW. This is known and has been designed into the spec as a _minimum_, not a recommendation, and is further secured by KDF* functions. The reason the _minimum_ is so low is to allow for situations that regular users find themselves in commonly: quickly and easily protecting themselves from common scammers. A 64 bit minimum means the setup messages can be encoded as easy to say (and enter) 12 digit numbers, one for each operator to enter. We believe that this is a fair balance between usability and security for for non-technical users with _this specific use case_. **MTOTP SUPPORTS MUCH MORE ENTROPY IF DESIRED**, up to 256 bits if each operator wants to share a handful of BIP39 words, or scan a QR code, or copy/paste a Base64URL string - all of these are supported (and recommended) if your use case calls for higher levels of security. 
>
> \* Technically Password-Based Key Derivation Functions, like Argon2id, but we're avoiding the use of the "PBKDF" term to avoid confusion between general purpose PBKDF and the PDKDF2 algorithm.

## Suggested Starting Points

If you're creating an implementation, start with X.

If you're reviewing this document, start with [Appendix A.](#appendix-a-rationale) to understand the goals and how they were achieved.

- [ ] Finish / reword this section 

## Table of Contents

- [1. Introduction](#1-introduction)
  - [1.1. Scope](#11-scope)
  - [1.2. Background](#12-background)
  - [1.3. MTOTP Process Overview](#13-mtotp-process-overview)
- [2. Notation and Terminology](#2-notation-and-terminology)
- [3. MTOTP Message Format](#3-mtotp-message-format)
  - [3.1. Common Binary Structure](#31-common-binary-structure)
    - [3.1.1. Initial Keying Material (IKM)](#311-initial-keying-material-ikm)
    - [3.1.2. Message Checksum](#312-message-checksum)
  - [3.2. Extended Format Headers](#32-extended-format-headers)
    - [3.2.1. Extended Format Version Header](#321-extended-format-version-header)
    - [3.2.2. Extended v1 Header Structure](#322-extended-v1-header-structure)
    - [3.2.3. Extended v1 KDF Algorithm](#323-extended-v1-kdf-algorithm)
    - [3.2.4. Extended v1 KDF Difficulty Scale](#324-extended-v1-kdf-difficulty-scale)
  - [3.3. Compact Format Headers](#33-compact-format-headers)
    - [3.3.1. Compact Format Binary Structure](#331-compact-format-binary-structure)
    - [3.3.2. Compact Format Version](#332-compact-format-version)
    - [3.3.3. Compact Format KDF Algorithm](#333-compact-format-kdf-algorithm)
    - [3.3.4. Compact Format KDF Difficulty](#334-compact-format-kdf-difficulty)
      - [3.3.4.1. Compact Format scrypt](#3341-compact-format-scrypt)
      - [3.3.4.2. Compact Format Argon2id](#3342-compact-format-argon2id)
- [4. MTOTP Message Encodings](#4-mtotp-message-encodings)
  - [4.1. Decimal Encoding](#41-decimal-encoding)
    - [4.1.1. Decimal Encode Procedure](#411-decimal-encode-procedure)
    - [4.1.2. Decimal Decode Procedure](#412-decimal-decode-procedure)
  - [4.2. BIP39 Word List Encoding](#42-bip39-word-list-encoding)
    - [4.2.1. BIP39 Encode Procedure](#421-bip39-encode-procedure)
    - [4.2.2. BIP39 Decode Procedure](#422-bip39-decode-procedure)
  - [4.3. Encoded String](#43-encoded-string)
    - [4.3.1. Base64URL Encode Procedure](#431-base64url-encode-procedure)
    - [4.3.2. Base64URL Decode Procedure](#432-base64url-decode-procedure)
- [5. Secret Derivation](#5-secret-derivation)
  - [5.1. IKM Identification](#51-ikm-identification)
  - [5.2. Capability Negotiation](#52-capability-negotiation)
  - [5.3. Key Derivation](#53-key-derivation)
  - [5.4. TOTP Application](#54-totp-application)
- [6. KDF Difficulty Scaling](#6-kdf-difficulty-scaling)
  - [6.1. PBKDF2-HMAC-SHA-256 Parameters](#61-pbkdf2-hmac-sha-256-parameters)
  - [6.2. Scrypt Parameters](#62-scrypt-parameters)
  - [6.3. Argon2id Parameters](#63-argon2id-parameters)
- [7. Clock Synchronization](#7-clock-synchronization)
- [8. Security Considerations](#8-security-considerations)
  - [8.1. MTOTP Message Exchange Channel](#81-mtotp-message-exchange-channel)
  - [8.2. Entropy and Key Strength](#82-entropy-and-key-strength)
  - [8.3. Key Derivation Rationale](#83-key-derivation-rationale)
  - [8.4. Clock and Replay Considerations](#84-clock-and-replay-considerations)
- [9. References](#9-references)
  - [9.1. Normative References](#91-normative-references)
  - [9.2. Informative References](#92-informative-references)
- [Appendix A. Rationale](#appendix-a-rationale)
  - [A.1. Decimal Encodings Rational](#a1-decimal-encodings-rational)
    - [A.1.1. Decimal Encoding and Compact Format](#a11-decimal-encoding-and-compact-format)
    - [A.1.2. Decimal Encoding: Message Length Derivation](#a12-decimal-encoding-message-length-derivation)
    - [A.1.3. Decimal Encoding: Floating-Point Arithmetic](#a13-decimal-encoding-floating-point-arithmetic)
  - [A.2. Key Derivation: Fixed Protocol Salt](#a2-key-derivation-fixed-protocol-salt)
  - [A.3. TOTP Parameter Compatibility](#a3-totp-parameter-compatibility)
  - [A.4. Difficulty Scale Rational](#a4-difficulty-scale-rational)
    - [A.4.1. Difficulty Scale Design Goals](#a41-difficulty-scale-design-goals)
    - [A.4.2. Attacker Cost Model](#a42-attacker-cost-model)
    - [A.4.3. Scale Definition](#a43-scale-definition)
    - [A.4.4. Baseline (Level 0)](#a44-baseline-level-0)
    - [A.4.5. Cross-Algorithm Equivalence](#a45-cross-algorithm-equivalence)
    - [A.4.6. PBKDF2 Historical Iteration Count Trajectory](#a46-pbkdf2-historical-iteration-count-trajectory)
    - [A.4.7. Scrypt Difficulty Scaling Rationale](#a47-scrypt-difficulty-scaling-rationale)
    - [A.4.8. Scrypt TMTO Resistance](#a48-scrypt-tmto-resistance)
    - [A.4.9. Argon2id Level Calibration](#a49-argon2id-level-calibration)
    - [A.4.10. Argon2id Historical Parameters Trajectory](#a410-argon2id-historical-parameters-trajectory)
    - [A.4.11. Argon2id TMTO Resistance](#a411-argon2id-tmto-resistance)
- [Appendix B. Examples](#appendix-b-examples)
  - [B.1. Decimal Encoding: IKM Bit Length Examples](#b1-decimal-encoding-ikm-bit-length-examples)
  - [B.2. Decimal Encoding: Symbol Count Examples](#b2-decimal-encoding-symbol-count-examples)
  - [B.3. Decimal Encoding: Message Bit Length Examples](#b3-decimal-encoding-message-bit-length-examples)

## TODOs

### TODOs Before Sharing Externally

#### Technical Issues

- Security Considerations > Security Analysis (at least a minimal one), including what we are protecting against and what we are not (eg: secure transfer of MTOTP messages is on the user). Claude wrote this based on the HOTP security analysis, even through I told it not to. I have not reviewed this and have little interest in reviewing it until the spec is complete (as I told Claude). Leaving it here because maybe it’ll be funny.   ([Section 8.](#8-security-considerations))
- Argon2id TMTO Resistance > VERIFY the math / accuracy of this section   ([Appendix A.4.11.](#a411-argon2id-tmto-resistance))

#### Documentation Issues

- [ ] Add references for [Appendix D.](#appendix-d-security-analysis): eprint.iacr.org/2017/603 (TMTO analysis of scrypt vs. Argon2id) and eprint.iacr.org/2015/430 (Argon2id design rationale). Confirm whether a standalone FIPS 180-4 citation is required for SHA-256 or whether citation through [RFC9106](https://www.rfc-editor.org/info/rfc9106) is sufficient.]]

- Key Derivation Rationale > Figure out what we were referring to when mentioning "Appendix B" and update text / link above.   ([Section 8.3.](#83-key-derivation-rationale))
- Appendix Rationale > Possibly add content here about the reasoning for always exactly filling up the $B_{ikm}$ section 100% (ie: no padding) but may not be necessary as it's briefly covered in the section 5 intro   ([Appendix A.](#appendix-a-rationale))
- Decimal Encoding and Compact Format > Figure out which section I was intending to link to and update the above "Section X" note (with link).   ([Appendix A.1.1.](#a11-decimal-encoding-and-compact-format))
- Cross-Algorithm Equivalence > Either remove this section or move it to the appendix   ([Appendix A.4.5.](#a45-cross-algorithm-equivalence))
- Appendix ABNF Grammar > Decide if needed and if so define formal ABNF per [RFC5234](https://www.rfc-editor.org/info/rfc5234) for:   > o  MTOTP message binary format (header, IKM, and checksum fields) > o  Decimal encoding (fixed-width digit string) > o  Encoded string format (MTOTP: prefix and base32 body) > o  JSON format (pending Section 4.4) ([Appendix E.](#appendix-e-abnf-grammar))

### TODOs Before Publicly Publishing

#### Technical Issues

- Message Checksum > Consider whether the checksum length should scale with message length. Longer messages provide more opportunity for transcription error; a longer checksum would provide proportionally stronger error detection at the cost of one bit of IKM entropy per additional checksum bit.   ([Section 3.1.2.](#312-message-checksum))
- Compact Format KDF Algorithm > If removing scrypt as an option, we can remove this bit and apply it to elsewhere (eg: a difficulty level, or a version) instead.   ([Section 3.3.3.](#333-compact-format-kdf-algorithm))
- Compact Format KDF Difficulty > "fixed to OWASP recommendations" is load-bearing text here — confirm specific parameter values before this document advances.   ([Section 3.3.4.](#334-compact-format-kdf-difficulty))
- Compact Format KDF Difficulty > consider whether a 1- or 2-bit difficulty hint is feasible within the overhead budget; see TODOs in 4.3.4.1 and 4.3.4.2.   ([Section 3.3.4.](#334-compact-format-kdf-difficulty))
- Compact Format scrypt > Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...? Or remove scrypt completely   ([Section 3.3.4.1.](#3341-compact-format-scrypt))
- Compact Format Argon2id > Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...?   ([Section 3.3.4.2.](#3342-compact-format-argon2id))
- Compact Format Argon2id > define the very nebulous concept of "If the specified difficulty level and entropy combined would create a secret too weak to provide proper security, the exchange MUST fail". The biggest risk being PBKDF, which is why it’s banned from compact mode which is designed for smaller amounts of entropy.   ([Section 3.3.4.2.](#3342-compact-format-argon2id))
- KDF Difficulty Scaling > Rebalance the KDF difficulty scaling based on actual device speeds (potentially use cloud phone rentals, to run tests on actual hardware far beyond what we could find)   ([Section 6.](#6-kdf-difficulty-scaling))
- PBKDF2-HMAC-SHA-256 Parameters > Confirm minimum combined IKM entropy for PBKDF2.   ([Section 6.1.](#61-pbkdf2-hmac-sha-256-parameters))
- Scrypt Parameters > Decide whether to retain scrypt.   ([Section 6.2.](#62-scrypt-parameters))
- Argon2id Parameters > Consider lowering $p$ to 1 for single-threaded devices.   ([Section 6.3.](#63-argon2id-parameters))
- Baseline Level 0 > We almost certainly want to lower the baseline / level 0 requirement to avoid preventing people with older devices from using the protocol. This document was written before we started gathering actual device stats. Once we've completed that, this scale will be updated to match.   ([Appendix A.4.4.](#a44-baseline-level-0))
- Appendix Test Vectors > Include test vectors that can be used to verify third party code. Generate and verify all test vectors once parameters are finalized.  Authors MUST verify all values; do not use placeholders as reference data.   ([Appendix C.](#appendix-c-test-vectors))
- Appendix Security Analysis > This appendix requires a dedicated writing session with verified GPU benchmarks.  Structure should be comparable to RFC 4226 Appendix A.   ([Appendix D.](#appendix-d-security-analysis))
- Appendix Reference Implementation > Include a reference implementation that others can test their code against ([Appendix F.](#appendix-f-reference-implementation)) https://www.ietf.org/rfc/rfc4226.txt / Include a JS? implementation of calculating everything, converting to/from binary, etc. https://www.ietf.org/rfc/rfc4226.txt   ([Appendix F.](#appendix-f-reference-implementation))

#### Documentation Issues

- Compact Format KDF Difficulty > Add info to [Appendix A.](#appendix-a-rationale) about this being famous last words all rolled up into one little section right here. 😭   ([Section 3.3.4.](#334-compact-format-kdf-difficulty))
- MTOTP Message Encodings > Add that apps MUST/SHOULD encourage the user NOT to share MTOTP messages over insecure channels. Cannot prevent it, but should be warned.    ([Section 4.](#4-mtotp-message-encodings))
- Scrypt Parameters > Define memory for each level more precisely.   ([Section 6.2.](#62-scrypt-parameters))
- Argon2id Parameters > Define memory for each level more precisely.   ([Section 6.3.](#63-argon2id-parameters))

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

Section 9 of [RFC4226](https://www.rfc-editor.org/info/rfc4226) describes a three-pass mutual authentication scheme using HOTP, in which the client presents a first one-time password, the server responds with a second, and the client verifies the server response. The TOTP equivalent requires one party to defer code presentation until the following 30-second time window, a constraint that is impractical for real-time interaction.

MTOTP addresses these issues by deriving two directional secrets from a pair of independently generated IKM values, one contributed by each party. The derivation uses the two IKM values in opposite concatenation orderings, such that both devices independently arrive at identical results. Alice’s outbound shared secret equals Bob’s inbound shared secret, and vice versa, without additional coordination after the initial MTOTP message exchange.

In addition, where standard TOTP provisioning relies on the `otpauth://` URI scheme transmitted via QR code or copy-paste, the exchange of the parameters and IKM values can be encoded into a single message that humans can comfortably read, convey, and transcribe. This makes the provisioning exchange viable over voice or other low-bandwidth channels where QR codes and digital copy-paste are unavailable.

### 1.3. MTOTP Process Overview

MTOTP extends TOTP by replacing the server-provisioned shared secret with two directional secrets derived from IKM contributed by both parties. Once established, the Shared Secrets are used identically to standard TOTP [RFC6238](https://www.rfc-editor.org/info/rfc6238).

Establishment requires both parties to exchange MTOTP messages. Each party constructs and transmits a message, then receives and processes the other party's message. Both steps MUST be completed before any TOTP authentication can occur. The order of exchange is not significant.

**Preparing an MTOTP Message to Send**
Select an encoding ([Section 4.](#4-mtotp-message-encodings)), construct the message ([Section 3.](#3-mtotp-message-format)), and have the user transmit it to the other party.

**Processing a Received MTOTP Message**
Decode and validate the received message ([Section 3.](#3-mtotp-message-format) and [Section 4.](#4-mtotp-message-encodings)), derive the Shared Secrets ([Section 5.](#5-secret-derivation)), and use each Shared Secret as key $K$ in TOTP [RFC6238](https://www.rfc-editor.org/info/rfc6238) per [Section 5.4.](#54-totp-application).

## 2. Notation and Terminology

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “NOT RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in RFC2119 when, and only when, they appear in all capitals, as shown here.

The following terms are used throughout this document:

**Operator:**<br />
The entity controlling a device participating in an MTOTP exchange. Operators are typically humans, but MAY be automated systems such as AI agents.

**Alice:**<br />
The local device and its operator. The roles of Alice and Bob are symmetric; each device considers itself Alice and its peer Bob. The labels are used for expository clarity and do not imply initiation order or protocol asymmetry.

**Bob:**<br />
The remote device and its operator.

**MTOTP message:**<br />
The binary structure exchanged between two devices during the MTOTP setup procedure.

**`Message_Alice` / `Message_Bob`:**<br />
The MTOTP messages generated by Alice and Bob’s devices.

**Input Keying Material (IKM):**<br />
The entropy bits generated by a device and contributed to the shared secret derivation process. The IKM does not include the protocol header or checksum fields of the MTOTP message.

**`IKM_Alice` / `IKM_Bob`:**<br />
The IKM fields of `Message_Alice` and `Message_Bob`.

**Compact Format:**<br />
The MTOTP message format defined in [Section 3.3.](#33-compact-format-headers) optimized for decimal encoding. Carries fixed KDF parameters.

**Extended Format:**<br />
The MTOTP message format defined in [Section 3.2.](#32-extended-format-headers), carrying explicit negotiated KDF algorithm and parameters.

**$B_{overhead}$:**<br />
The number of bits occupied by the message header and checksum fields.

**$B_{min}$:**<br />
The minimum IKM entropy requested by the implementation, in bits.

**$B_{ikm}$:**<br />
The actual IKM length generated, in bits. Always greater than or equal to $B_{min}$, rounded up to the next symbol boundary for the chosen encoding.

**$B_{message}$:**<br />
The total message length in bits, equal to $B_{overhead} + B_{ikm}$.

**$C$:**<br />
The bits-per-symbol value for the chosen encoding.

**$N_S$:**<br />
The number of symbols in the encoded message.

**Password-Based Key Derivation Function (KDF):**<br />
A cryptographic function used to derive a Shared Secret from the combined IKM entropy. Referred in this document as just "KDF" to avoid confusion with the PBKDF2 Algorithm.

**Shared Secrets:**<br />
The TOTP keys derived from the combined IKM values of both parties. Two Shared Secrets are produced per MTOTP message exchange, one per direction of verification. Each Shared Secret serves as the key $K$ in the TOTP computation as defined in [RFC4226](https://www.rfc-editor.org/info/rfc4226) and [RFC6238](https://www.rfc-editor.org/info/rfc6238).

**`SharedSecret_out`:**<br />
The derived TOTP key used by Alice to generate codes presented to Bob.

**`SharedSecret_in`:**<br />
The derived TOTP key used by Alice to verify codes presented by Bob.

**$K$:**<br />
The TOTP shared secret key, as defined in [RFC6238](https://www.rfc-editor.org/info/rfc6238). In MTOTP, $K$ is either `SharedSecret_out` or `SharedSecret_in` depending on direction.

**$T$:**<br />
The time step counter, as defined in [RFC6238](https://www.rfc-editor.org/info/rfc6238).

## 3. MTOTP Message Format

### 3.1. Common Binary Structure

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
| `0`   | Extended Format. See [Section 3.2.](#32-extended-format-headers). |
| `1`   | Compact Format. See [Section 3.3.](#33-compact-format-headers).   |

**Format-Specific Headers (variable):**
Present in all messages.  Structure depends on the value of the Message Format bit. See [Section 3.2.](#32-extended-format-headers) and [Section 3.3.](#33-compact-format-headers).

**IKM Bits (variable):**
Initial Keying Material. See [Section 3.1.1.](#311-initial-keying-material-ikm).

**Message Checksum (5 bits):**
Occupies the five least significant bits of every MTOTP message. See [Section 3.1.2.](#312-message-checksum).

#### 3.1.1. Initial Keying Material (IKM)

The IKM field MUST contain a minimum number of bits of entropy generated by a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086). 

IKM length is not a completely free parameter — it is determined by the choice of encoding, message format, and encoding length. The IKM field occupies all remaining bits after the headers and checksum for the message format in use.

Each encoding has a natural granularity: a minimum bit size and step size that the total message length must be a multiple of. For example, BIP39 words each represent 11 bits, so valid message lengths are 11, 22, 33, 44 bits and so on — no intermediate lengths are possible. Once an encoding is chosen, implementations MUST use the maximum IKM length that fits within the encoding's natural granularity, and MUST NOT transmit fewer bits of entropy than the encoding can carry. Doing so would reduce the entropy of the exchange without reducing its size.

Formulas to calculate the encoding granularity for each supported encoding, along with examples, are defined in [Section 4.](#4-mtotp-message-encodings).

The minimum combined IKM entropy for an exchange is 64 bits (32 bits per device). Implementations MUST verify the combined IKM length and MUST reject any message that would result in less than 64 bits of combined IKM entropy.

> **Note (Non-Normative):** A minimum combined entropy of 64 bits is intentionally low by cryptographic standards. This reflects a deliberate usability tradeoff for one specific use case of MTOTP: allowing users who are not technically sophisticated to establish a shared secret by exchanging a short numeric string. MTOTP is fully capable of carrying much higher entropy — longer codes, BIP39 words, or Base64URL strings are strongly encouraged where usability permits. The KDF step is specifically chosen and parameterised to harden low-entropy inputs against brute-force attack.

#### 3.1.2. Message Checksum

The five least significant bits of every MTOTP message are the checksum field. This field is computed identically across all message formats, permitting any implementation to validate the checksum prior to decoding the message content.

The checksum additionally serves a limited domain-separation role. Because MTOTP messages carry no dedicated magic number or protocol identifier, the domain-separated HMAC-SHA256 key "MTOTP-v0" makes the checksum distribution distinct from raw SHA-256 output. This reduces — but does not eliminate — the probability that output from an unrelated system is accepted as a valid MTOTP message.

Let B denote the concatenation of all bits preceding the checksum (i.e., including the format bit, all header bits, and the IKM bits), zero-padded on the right to the nearest byte boundary.  The checksum is computed as:

```
checksum_bits = MSB5(HMAC-SHA256("MTOTP-v0", B))
```

where HMAC-SHA256 is as defined in [RFC4231](https://www.rfc-editor.org/info/rfc4231), MSB5(x) denotes the five most significant bits of the first byte of x, and the HMAC key is the ASCII encoding of the literal string "MTOTP-v0".

Implementations MUST verify the checksum upon decoding an MTOTP message and MUST reject any message that fails verification.

- [ ] Consider whether the checksum length should scale with message length. Longer messages provide more opportunity for transcription error; a longer checksum would provide proportionally stronger error detection at the cost of one bit of IKM entropy per additional checksum bit.  

### 3.2. Extended Format Headers

This format is intended for exchange channels with capacity for additional metadata, such as BIP39 word list, 2D barcode, or encoded string exchange. 

#### 3.2.1. Extended Format Version Header

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
| `01`  | Version 1. See [Section 3.2.2.](#322-extended-v1-header-structure). |
| `10`  | Reserved.                                                        |
| `11`  | Reserved.                                                        |
| `00`  | Reserved.                                                        |

Version numbering begins at `01` rather than `00` so that any valid Extended message is guaranteed to contain a `1` bit within the first three bits, ensuring the binary value is never ambiguous when reconstructed from decimal encoding. See [Section 4.1.](#41-decimal-encoding). Values `00`, `10`, and `11` are reserved for future protocol enhancements or KDF algorithm updates. 

**Version-Specific Headers (variable):**
Structure depends on the Extended Version field.  This document specifies Version 1 only.  See [Section 3.2.2.](#322-extended-v1-header-structure).

A receiver that encounters an Extended Version value it does not recognise or support MUST NOT attempt to parse the remainder of the message, MUST reject the message, and MUST inform the user that the peer device uses an unsupported version of the protocol.

#### 3.2.2. Extended v1 Header Structure

```
Version 01 Headers {
  KDF Algorithm (3 bits),
  KDF Difficulty Scale (3 bits),
}
```

**KDF Algorithm (3 bits):**
See [Section 3.2.3.](#323-extended-v1-kdf-algorithm).

**KDF Difficulty (3 bits):**
See [Section 3.2.4.](#324-extended-v1-kdf-difficulty-scale).

**The total message overhead for Extended Format Version 1 is 14 bits:**

| Field            | Bits   |
| ---------------- | ------ |
| Message Format   | 1      |
| Extended Version | 2      |
| KDF Algorithm    | 3      |
| KDF Difficulty   | 3      |
| Message Checksum | 5      |
| **Total**        | **14** |

#### 3.2.3. Extended v1 KDF Algorithm

Each bit in the KDF Algorithm field indicates support for one algorithm. A device MUST set each bit corresponding to an algorithm it supports. More than one bit MAY be set.

| Value | Algorithm                                                              |
| ----- | ---------------------------------------------------------------------- |
| `001` | PBKDF2-HMAC-SHA-256 [RFC8018](https://www.rfc-editor.org/info/rfc8018) |
| `010` | scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914)              |
| `100` | Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106)            |

The negotiated algorithm is the highest-security algorithm for which both devices have set the corresponding bit. The security ordering from lowest to highest is: PBKDF2-HMAC-SHA-256, scrypt, Argon2id.  If no algorithm bit is set in common by both devices, the exchange MUST fail.

- [ ] Consider adding a section for the above paragraph (ie: "how to choose the common kdf algorithm") instead of embedding it in the header description.  

PBKDF2-HMAC-SHA-256 is included solely for environments with FIPS-140 compliance requirements and is considered the weakest of the three supported algorithms. Implementations SHOULD support at least one of scrypt or Argon2id in addition to PBKDF2, ensuring that PBKDF2 is only negotiated when the peer device supports no stronger algorithm. See [Section 6.1.](#61-pbkdf2-hmac-sha-256-parameters).

#### 3.2.4. Extended v1 KDF Difficulty Scale

The three-bit Difficulty Scaling field encodes an integer value in the range 0–7 (binary `000`–`111`). This value is interpreted as an index into a per-algorithm difficulty parameter table, as specified in [Section 6.](#6-kdf-difficulty-scaling). The same index value applies regardless of the negotiated KDF algorithm; the corresponding parameters for the negotiated algorithm are selected from that algorithm's table.

### 3.3. Compact Format Headers

The Compact Format trades configurability for minimal overhead, using fixed KDF Difficulty to preserve as many bits as possible for entropy. It is intended for constrained exchange channels and for users who are uncomfortable with phrase-based entry, preferring to enter a short numeric string on a keypad rather than a word list or encoded string. This is an explicit usability tradeoff: the reduced overhead provides enough security for casual or non-mission-critical use cases, but implementations SHOULD prefer Extended Format where the exchange channel and user comfort permit.

With a 32-bit IKM, the total message length — comprising all header fields, the IKM, and the 5-bit checksum — is 39 bits, giving a maximum decimal value of 2^39 - 1 = 549,755,813,887, which fits within 12 decimal digits.

#### 3.3.1. Compact Format Binary Structure

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

#### 3.3.2. Compact Format Version

The Compact Format contains no version field. Version omission is intentional; the saved bits are allocated to entropy.

#### 3.3.3. Compact Format KDF Algorithm

The Compact Format uses a single bit to indicate the highest-security algorithm the device supports. An implementation MUST support scrypt in order to support Compact Format; scrypt is the baseline and cannot be omitted.

- [ ] If removing scrypt as an option, we can remove this bit and apply it to elsewhere (eg: a difficulty level, or a version) instead.   

| Value | scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914) | Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106) |
| ----- | --------------------------------------------------------- | ----------------------------------------------------------- |
| `0`   | Supported                                                 | Not supported                                               |
| `1`   | Supported                                                 | Supported                                                   |

A device that sets this bit to `1` implicitly supports scrypt as a fallback, ensuring that negotiation succeeds with any compliant peer.

PBKDF2-HMAC-SHA-256 is explicitly prohibited in Compact Format. Compact Format provides less entropy than Extended Format by design, and PBKDF2 is insufficiently resistant to brute-force attacks against low-entropy sources. An implementation MUST NOT negotiate PBKDF2 in Compact Format under any circumstances, including interoperability with a peer that does not support scrypt or Argon2id. In such cases, the exchange MUST fail.

#### 3.3.4. Compact Format KDF Difficulty

To conserve space and account for the reduced entropy available in Compact Format, KDF Difficulty is fixed rather than negotiated. Parameters are chosen conservatively, following current OWASP recommendations. 

- [ ] "fixed to OWASP recommendations" is load-bearing text here — confirm specific parameter values before this document advances.  
- [ ] consider whether a 1- or 2-bit difficulty hint is feasible within the overhead budget; see TODOs in 4.3.4.1 and 4.3.4.2.  
- [ ] Add info to [Appendix A.](#appendix-a-rationale) about this being famous last words all rolled up into one little section right here. 😭  

##### 3.3.4.1. Compact Format scrypt

- [ ] Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...? Or remove scrypt completely  

##### 3.3.4.2. Compact Format Argon2id

- [ ] Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...?   

If the specified difficulty level and entropy combined would create a secret too weak to provide proper security, the exchange MUST fail. 

- [ ] define the very nebulous concept of "If the specified difficulty level and entropy combined would create a secret too weak to provide proper security, the exchange MUST fail". The biggest risk being PBKDF, which is why it’s banned from compact mode which is designed for smaller amounts of entropy.   

## 4. MTOTP Message Encodings

The binary MTOTP message is the normative form; the encodings defined in this section are representations of that binary value that are more easily transmitted by humans.

Each encoding defines a bits-per-symbol value $C$ and a symbol unit (digits, words, or characters). The value of $C$ for each encoding is defined in its respective subsection ([Section 4.1.](#41-decimal-encoding), [Section 4.2.](#42-bip39-word-list-encoding), [Section 4.3.](#43-encoded-string)). The formulas below use these values and apply to all encodings.

**IKM Bit Length.** The encoded message must fit exactly into a whole number of symbols, with no partial symbols and no padding. Because the length of the IKM is not transmitted, the decoder re-derives it from $N_S$ — this is only possible if the encoder always fills the encoding completely. Choose a minimum IKM length $B_{min}$ (in bits). The actual IKM length $B_{ikm}$ is the smallest value greater than or equal to $B_{min}$ that satisfies this constraint:

$$B_{ikm} = \left\lfloor \left\lceil (B_{overhead} + B_{min}) \times \frac{1}{C} \right\rceil \times C \right\rfloor - B_{overhead}$$

**Message Bit Length.** On decode, count the number of symbols (digits, words, or characters) received ($N_S$) and calculate the number of bits in the message as:

$$B_{message} = \left\lfloor N_S \times C \right\rfloor$$

For encodings with integer $C$, this is exact. For decimal, where $C=log⁡_{2}(10)$, the floor resolves the fractional remainder.

> See [Appendix B.1.](#b1-decimal-encoding-ikm-bit-length-examples) for examples.

Implementations MUST reject and MUST NOT generate any encoding where $B_{min} < 32$ (see [Section 3.1.1.](#311-initial-keying-material-ikm).

- [ ] Add that apps MUST/SHOULD encourage the user NOT to share MTOTP messages over insecure channels. Cannot prevent it, but should be warned.   

### 4.1. Decimal Encoding

Decimal encoding represents an MTOTP message as a string of decimal digits, suitable for voice exchange or manual entry on a numeric keypad. 

> Decimal encoding is designed for use with Compact format (see [Appendix A.1.1.](#a11-decimal-encoding-and-compact-format)).

For this encoding, $C = \log_2(10)$.

> See [Appendix A.1.3.](#a13-decimal-encoding-floating-point-arithmetic) for implementation notes on floating-point evaluation of this value.

Formatting characters such as spaces or hyphens MAY be added for readability and MUST be stripped before decoding. Implementations MUST NOT restrict digit input to a fixed length, and MUST reject input of fewer than 12 digits (which would result in $B_{ikm}<32$). The message length is determined by the digit count after stripping formatting characters, and is validated during decoding per [Section 3.](#3-mtotp-message-format).

> See [Appendix B.1.](#b1-decimal-encoding-ikm-bit-length-examples) for examples.

#### 4.1.1. Decimal Encode Procedure

An implementation SHALL encode an MTOTP binary message to a decimal string as follows:

1. Determine the format (Compact or Extended) and minimum desired IKM entropy $B_{min}$ (in bits).
2. Calculate $B_{ikm}$ per [Section 4.](#4-mtotp-message-encodings).
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086).
4. Construct the complete MTOTP binary message per [Section 3.](#3-mtotp-message-format).
5. Interpret the binary message as a single non-negative integer in big-endian byte order, where the first byte is the most significant. Within each byte, bit 7 is the most significant bit. Implementations MUST use arbitrary-precision unsigned integer arithmetic and MUST NOT use fixed-width integer types (e.g., uint64) as an intermediate representation, as the message integer may exceed 64 bits.
6. Express the integer as a decimal digit string, left-padded with zeros to exactly $N_S$ digits, where $N_S$ is calculated per [Section 4.](#4-mtotp-message-encodings). The resulting string MUST contain exactly $N_S$ characters, each in the range `0`-`9`. Leading zeros are significant and MUST be preserved; omitting them would alter the binary value they represent.

#### 4.1.2. Decimal Decode Procedure

An implementation SHALL decode an MTOTP decimal string to a binary message as follows:

1. Strip all formatting characters. Any character outside the range `0`-`9` MUST be removed before processing.
2. Count the remaining characters to obtain $N_S$.
3. Calculate $B_{message}$ per [Section 4.](#4-mtotp-message-encodings).
4. Parse the digit string as a single non-negative integer using arbitrary-precision unsigned integer arithmetic. Implementations MUST NOT use fixed-width integer types (e.g., uint64) as an intermediate representation.
5. If the parsed integer requires more bits than $B_{message}$ to represent, the message is malformed and the implementation MUST reject it with an error.
6. Serialize the integer to exactly $\lceil B_{message} / 8 \rceil$ bytes in big-endian order, zero-padded on the left. This is the MTOTP binary message.
7. Validate and decode the MTOTP binary message per [Section 3.](#3-mtotp-message-format).

> See [Appendix A.1.2.](#a12-decimal-encoding-message-length-derivation) for notes on message length derivation.

### 4.2. BIP39 Word List Encoding

BIP39 word list encoding represents an MTOTP message as a sequence of words drawn from the BIP39 word list [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki), suitable for spoken or text-based exchange.

For this encoding, $C = 11$. Each word in the BIP39 word list corresponds to exactly 11 bits.

Note: This encoding uses the BIP39 word list as an encoding alphabet only. It does not implement the BIP39 standard [BIP39]. In particular, implementations MUST NOT apply or verify a BIP39 checksum; message integrity is provided solely by the MTOTP checksum ([Section 3.1.2.](#312-message-checksum)).

#### 4.2.1. BIP39 Encode Procedure

An implementation SHALL encode an MTOTP binary message to a BIP39 word sequence as follows:

1. Determine the format (Compact or Extended) and minimum desired IKM entropy $B_{min}$ (in bits).
2. Calculate $B_{ikm}$ per [Section 4.](#4-mtotp-message-encodings).
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086).
4. Construct the complete MTOTP binary message per [Section 3.](#3-mtotp-message-format).
5. Read the message bits from most significant to least significant, taking 11 bits at a time.
6. For each 11-bit group, interpret it as an unsigned integer in the range 0–2047 and select the corresponding entry from the BIP39 word list.

#### 4.2.2. BIP39 Decode Procedure

An implementation SHALL decode a BIP39 word sequence to an MTOTP binary message as follows:

1. For each word in the input sequence, locate its index in the BIP39 word list. If any word is not found, the message is malformed and the implementation MUST reject it.
2. Concatenate the 11-bit binary representations of the word indices, from first word to last. This is the MTOTP binary message.
3. Validate and decode the MTOTP binary message per [Section 3.](#3-mtotp-message-format).

### 4.3. Encoded String

Encoded string format represents an MTOTP message as a Base64URL-encoded string [RFC4648](https://www.rfc-editor.org/info/rfc4648), suitable for copy-paste over digital channels and for use as a URI or app intent.

For this encoding, $C = 6$.

Format:
```
MTOTP;base64url,<data>
```

`<data>` is the MTOTP binary message encoded as Base64URL per [RFC4648](https://www.rfc-editor.org/info/rfc4648) [Section 4.](#4-mtotp-message-encodings). The prefix `MTOTP;base64url,` is case-sensitive. Decoders MUST reject strings that do not conform to this format.

#### 4.3.1. Base64URL Encode Procedure

An implementation SHALL encode an MTOTP binary message to a Base64URL string as follows:

1. Determine the format (Compact or Extended) and minimum desired IKM entropy $B_{min}$ (in bits).
2. Calculate $B_{ikm}$ per [Section 4.](#4-mtotp-message-encodings).
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086).
4. Construct the complete MTOTP binary message per [Section 3.](#3-mtotp-message-format).
5. Encode the binary message as Base64URL per [RFC4648](https://www.rfc-editor.org/info/rfc4648) §5 (URL and Filename Safe Alphabet).
6. Prepend the ASCII prefix `MTOTP;base64url,` to produce the encoded string.

An encoded string MAY be represented as a QR code using any conformant QR code encoder for in-person or camera-based exchange. No additional specification is required for QR encoding.

#### 4.3.2. Base64URL Decode Procedure

An implementation SHALL decode a Base64URL encoded string to an MTOTP binary message as follows:

1. Verify the string begins with the ASCII prefix `MTOTP;base64url,`. If not, the message is malformed and the implementation MUST reject it with an error.
2. Strip the prefix to obtain the Base64URL encoded data.
3. Decode the Base64URL data per [RFC4648](https://www.rfc-editor.org/info/rfc4648) §5 (URL and Filename Safe Alphabet). The resulting bit string is the MTOTP binary message.
4. Validate and decode the MTOTP binary message per [Section 3.](#3-mtotp-message-format).

## 5. Secret Derivation

### 5.1. IKM Identification

Both `Message_Alice`​ and `Message_Bob` must be known before derivation begins. The IKM field of each message is identified per the binary structure defined in [Section 3.1.](#31-common-binary-structure).

Let:

```
IKM_Alice = the IKM field of Message_Alice
IKM_Bob = the IKM field of Message_Bob
```

Only the IKM fields are used as inputs to the derivation. The header and checksum fields do not contribute to the entropy of the derived secrets.

If `|IKM_Alice| + |IKM_Bob| < 64` bits, derivation MUST fail with an error.

### 5.2. Capability Negotiation

Each party advertises a bitmask of supported KDF algorithms (3 bits) and a maximum supported difficulty level (3 bits, value 0–7), as carried in the MTOTP message header per [Section 3.](#3-mtotp-message-format).

Negotiation proceeds as follows:

1. Select the strongest algorithm supported by both parties, in preference order Argon2id > scrypt > PBKDF2-HMAC-SHA-256. If no algorithm is supported by both parties, the exchange MUST fail.
2. Select the lower of the two advertised maximum difficulty levels for the selected algorithm. The selected KDF parameters are defined in [Section 6.](#6-kdf-difficulty-scaling).
3. If PBKDF2-HMAC-SHA-256 is selected, the selected algorithm's minimum entropy requirements MUST be verified per [Section 6.1.](#61-pbkdf2-hmac-sha-256-parameters) before proceeding. If not met, the exchange MUST fail.

### 5.3. Key Derivation

The KDF algorithm and difficulty level are determined by capability negotiation per [Section 5.2.](#52-capability-negotiation) and [Section 6.](#6-kdf-difficulty-scaling). 

The protocol salt `MTOTP-v0` is a fixed ASCII string providing domain separation between protocol versions. It is not secret and does not contribute entropy.

> See [Appendix A.2.](#a2-key-derivation-fixed-protocol-salt) for rationale on the use of a fixed protocol salt.

Two 256-bit Shared Secrets are derived:

```
SharedSecret_out = KDF(
	IKM_Alice || IKM_Bob, 
	salt="MTOTP-v0", 
	length=256, 
	<parameters>
)

SharedSecret_in = KDF(
	IKM_Bob || IKM_Alice, 
	salt="MTOTP-v0", 
	length=256, 
	<parameters>
)
```

The Shared Secrets are derived once at provisioning time and reused for all subsequent TOTP authentications.

### 5.4. TOTP Application

The two Shared Secrets are assigned directionally. From Alice's perspective:

- `SharedSecret_out` is used as TOTP key $K$ to generate codes presented to Bob.
- `SharedSecret_in` is used as TOTP key $K$ to verify codes presented by Bob.

Both parties perform the same derivation. Each device treats its own IKM as `IKM_Alice` and the peer's IKM as `IKM_Bob`. The result is that both parties independently arrive at matching directional keys without additional coordination.

Each Shared Secret is used as key $K$ in TOTP [RFC6238](https://www.rfc-editor.org/info/rfc6238):

$$TOTP(K, T) = HOTP(K, T)$$

where $T$ is the time step counter as defined in [RFC6238](https://www.rfc-editor.org/info/rfc6238). The following parameters are fixed by this specification and are not subject to negotiation. Both parties MUST use these parameters:

| Parameter      | Value                                |
| -------------- | ------------------------------------ |
| Hash algorithm | HMAC-SHA-256 [RFC2104](https://www.rfc-editor.org/info/rfc2104)               |
| Time step (X)  | 30 seconds                           |
| T0             | Unix epoch (1970-01-01 00:00:00 UTC) |
| Output digits  | 6                                    |

> See [Appendix A.3.](#a3-totp-parameter-compatibility) for rationale on the choice of TOTP parameters.

Implementations MUST comply with [RFC6238](https://www.rfc-editor.org/info/rfc6238) for all TOTP computation, including time step calculation, dynamic truncation, and output formatting.

## 6. KDF Difficulty Scaling

The three-bit difficulty field encodes a level in the range 0–7. This value indexes into a per-algorithm parameter table. Parameters are fully specified; no runtime derivation is performed. Both parties MUST produce identical parameters from identical inputs.

> See [Appendix A.4.](#a4-difficulty-scale-rational) for the rationale behind the difficulty scale design.

> **Implementation Note (Non-Normative):** Implementations SHOULD benchmark each supported KDF on first launch and select the highest difficulty level that is estimated to complete within 1–2 seconds on the device.

- [ ] Rebalance the KDF difficulty scaling based on actual device speeds (potentially use cloud phone rentals, to run tests on actual hardware far beyond what we could find)  

### 6.1. PBKDF2-HMAC-SHA-256 Parameters

PBKDF2 [RFC8018](https://www.rfc-editor.org/info/rfc8018) is included solely to satisfy regulatory requirements that mandate FIPS 140-validated KDFs. Because PBKDF2-HMAC-SHA-256 is not memory-hard, a minimum combined IKM entropy of 80 bits is REQUIRED when PBKDF2 is negotiated. If this requirement is not met, the exchange MUST fail.

- [ ] Confirm minimum combined IKM entropy for PBKDF2.  

| Level | Iterations     |
| ----- | -------------- |
| 0     | 1,000,000      |
| 1     | 4,000,000      |
| 2     | 16,000,000     |
| 3     | 64,000,000     |
| 4     | 256,000,000    |
| 5     | 1,024,000,000  |
| 6     | 4,096,000,000  |
| 7     | 16,384,000,000 |

> See [Appendix A.4.6.](#a46-pbkdf2-historical-iteration-count-trajectory).

### 6.2. Scrypt Parameters

Parameters: $N$ = cost parameter (power of 2 per [RFC7914](https://www.rfc-editor.org/info/rfc7914)), $r = 8$, $p = 1$.

| Level | $log_{2}(N)$ | Memory ($128 \times N \times r$ bytes) |
| ----- | ------------ | -------------------------------------- |
| 0     | 15           | 32 MiB                                 |
| 1     | 16           | 64 MiB                                 |
| 2     | 17           | 128 MiB                                |
| 3     | 18           | 256 MiB                                |
| 4     | 19           | 512 MiB                                |
| 5     | 20           | 1 GiB                                  |
| 6     | 21           | 2 GiB                                  |
| 7     | 22           | 4 GiB                                  |

> See [Appendix A.4.7.](#a47-scrypt-difficulty-scaling-rationale) and [Appendix A.4.8.](#a48-scrypt-tmto-resistance).

- [ ] Decide whether to retain scrypt.   
- [ ] Define memory for each level more precisely.  

### 6.3. Argon2id Parameters

Parameters: $m$ = memory in KiB, $t$ = iterations, $p$ = lanes [RFC9106](https://www.rfc-editor.org/info/rfc9106).

Variant: Argon2id, version 0x13.

| Level | $m$ (MiB) | $t$ | $p$ |
| ----- | --------- | --- | --- |
| 0     | 64        | 2   | 4   |
| 1     | 128       | 4   | 4   |
| 2     | 256       | 8   | 4   |
| 3     | 512       | 16  | 4   |
| 4     | 1024      | 32  | 4   |
| 5     | 2048      | 64  | 4   |
| 6     | 4096      | 128 | 4   |
| 7     | 8192      | 256 | 4   |

> See [Appendix A.4.9.](#a49-argon2id-level-calibration) and [Appendix A.4.11.](#a411-argon2id-tmto-resistance).

- [ ] Consider lowering $p$ to 1 for single-threaded devices.  
- [ ] Define memory for each level more precisely.  

## 7. Clock Synchronization

Correct TOTP operation requires that both devices maintain accurate Unix time.  Implementations SHOULD follow the clock synchronization and resynchronization guidance in [RFC6238](https://www.rfc-editor.org/info/rfc6238), including acceptance of codes from adjacent time steps.

## 8. Security Considerations

- [ ] Security Analysis (at least a minimal one), including what we are protecting against and what we are not (eg: secure transfer of MTOTP messages is on the user). Claude wrote this based on the HOTP security analysis, even through I told it not to. I have not reviewed this and have little interest in reviewing it until the spec is complete (as I told Claude). Leaving it here because maybe it’ll be funny.  

### 8.1. MTOTP Message Exchange Channel

The security of MTOTP depends on the confidentiality of the MTOTP message exchange.  An adversary who obtains both `Message_Alice` and `Message_Bob` can derive both Shared Secrets and impersonate either party.

Implementations SHOULD instruct users to exchange MTOTP messages only over channels where third-party interception is unlikely, such as a direct voice call, in-person exchange, or an end-to-end encrypted channel.  The HOTP specification [RFC4226](https://www.rfc-editor.org/info/rfc4226) requires OTP values to be transmitted over secure channels such as TLS or IPsec; MTOTP cannot mandate a channel type for MTOTP message exchange, as this exchange is out-of-band and under user control.

An active adversary substituting both MTOTP messages must have control of the exchange channel at the time of exchange.  Voice channels where speakers authenticate each other by voice recognition reduce the practical feasibility of this attack.

### 8.2. Entropy and Key Strength

The combined entropy available to the derived Shared Secrets is bounded by the sum of the entropies of `IKM_Alice` and `IKM_Bob`. For compact format messages with a 32-bit IKM, the combined entropy is 64 bits.

Implementations MUST use a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086) to generate IKM values.  A low-entropy contribution from either party reduces the security of both Shared Secrets .

Implementations SHOULD inform users when the combined entropy level of their exchange may be insufficient for high-security applications.

### 8.3. Key Derivation Rationale

The KDF options in both message versions reflect resistance to GPU and ASIC-accelerated brute-force attacks, adjusted for time-memory tradeoff (TMTO) cost.

scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914) is memory-hard, which limits GPU parallelism. However, scrypt is subject to a TMTO vulnerability in which an attacker using reduced memory incurs only a sub-linear time penalty.  See [Appendix D.](#appendix-d-security-analysis).

Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106) provides improved TMTO resistance over scrypt. Its data-dependent memory access pattern requires super-linear additional computation when memory is reduced, and inter-lane dependencies prevent independent parallel attacks. See Appendix B.

- [ ] Figure out what we were referring to when mentioning "Appendix B" and update text / link above.   

Compact format fixed parameters are selected to meet or exceed the OWASP minimum configurations [OWASP] for each algorithm, while
remaining practical on memory-constrained mobile platforms. Extended format permits explicit parameter selection across the full range of configurations recommended by [RFC9106](https://www.rfc-editor.org/info/rfc9106) and [OWASP], including values appropriate for server and desktop deployments.

The fixed protocol salt “MTOTP-v0” ([Section 5.](#5-secret-derivation)) provide domain separation but does not increase the entropy of the IKM inputs.

### 8.4. Clock and Replay Considerations

TOTP codes are valid only within the time step in which they are generated.  Implementations SHOULD follow the replay prevention guidance of [RFC6238](https://www.rfc-editor.org/info/rfc6238), including rejection of previously accepted OTP values within the current time step.

## 9. References

### 9.1. Normative References

[RFC9106]  Biryukov, A., Dinu, D., Khovratovich, D., and S. Josefsson, "Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work Applications", RFC 9106, September 2021.

[RFC5234]  Crocker, D. and P. Overell, "Augmented BNF for Syntax Specifications: ABNF", RFC 5234, January 2008.

[RFC6238]  M'Raihi, D., Machani, S., Pei, M., and J. Rydell, "TOTP: Time-Based One-Time Password Algorithm", RFC 6238, May 2011.

[RFC4226]  M'Raihi, D., Bellare, M., Hoornaert, F., Naccache, D., and O. Ranen, "HOTP: An HMAC-Based One-Time Password Algorithm", RFC 4226, December 2005.

[RFC4086]  Eastlake 3rd, D., Schiller, J., and S. Crocker, "Randomness Requirements for Security", RFC 4086, June 2005.

[RFC4231]  Nystrom, M., "Identifiers and Test Vectors for HMAC-SHA-224, HMAC-SHA-256, HMAC-SHA-384, and HMAC-SHA-512", RFC 4231, December 2005.

[RFC8018]  Moriarty, K., Kaliski, B., and A. Rusch, "PKCS #5: Password-Based Cryptography Specification Version 2.1", RFC 8018, January 2017.

[RFC7914]  Percival, C. and S. Josefsson, "The scrypt Password-Based Key Derivation Function", RFC 7914, August 2016.

[RFC4648]  Josefsson, S., "The Base16, Base32, and Base64 Data Encodings", RFC 4648, October 2006.

[RFC2104]  Krawczyk, H., Bellare, M., and R. Canetti, "HMAC: Keyed-Hashing for Message Authentication", RFC 2104, February 1997.

[RFC2898]  Kaliski, B., "PKCS #5: Password-Based Cryptography Specification Version 2.0", RFC 2898, September 2000.

### 9.2. Informative References

[BIP39]    "bips/bip-0039.mediawiki at master · bitcoin/bips · GitHub", https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki.

[OWASP Guide 2002]  "Chapter6.Authentication", https://web.archive.org/web/20021021080619/http://www.owasp.org/guide/v11/ch06.html#id2858301.

[OWASP Guide 2008]  "Guide to Authentication - OWASP", https://web.archive.org/web/20080914005739/http://www.owasp.org/index.php/Guide_to_Authentication#Best_Practices.

[OWASP Guide 2010]  "Guide to Authentication - OWASP", https://web.archive.org/web/20100718034930/http://www.owasp.org/index.php/Guide_to_Authentication#Minimum_hash_strength.

[OWASP Guide 2011]  "Password Storage Cheat Sheet - OWASP", https://web.archive.org/web/20111008022356/https://www.owasp.org/index.php/Password_Storage_Cheat_Sheet.

[OWASP Guide 2014]  "Password Storage Cheat Sheet - OWASP", https://web.archive.org/web/20140811055758/https://www.owasp.org/index.php/Password_Storage_Cheat_Sheet.

[OWASP Cheatsheet 2019]  "CheatSheetSeries/cheatsheets/Password_Storage_Cheat_Sheet.md at 2f976f1671c6cb4e9ce9fd8cbb59cf17f31b390e · OWASP/CheatSheetSeries · GitHub", https://github.com/OWASP/CheatSheetSeries/blob/2f976f1671c6cb4e9ce9fd8cbb59cf17f31b390e/cheatsheets/Password_Storage_Cheat_Sheet.md.

[OWASP Cheatsheet 2021]  "CheatSheetSeries/cheatsheets/Password_Storage_Cheat_Sheet.md at 986415b473402de66612dec5cd0b9b896ba6a7c6 · OWASP/CheatSheetSeries · GitHub", https://github.com/OWASP/CheatSheetSeries/blob/986415b473402de66612dec5cd0b9b896ba6a7c6/cheatsheets/Password_Storage_Cheat_Sheet.md.

[OWASP Cheatsheet 2023]  "CheatSheetSeries/cheatsheets/Password_Storage_Cheat_Sheet.md at f14bc4c0578e1328c23094dcb0a1d8e9b778b3ec · OWASP/CheatSheetSeries · GitHub", https://github.com/OWASP/CheatSheetSeries/blob/f14bc4c0578e1328c23094dcb0a1d8e9b778b3ec/cheatsheets/Password_Storage_Cheat_Sheet.md.

[OWASP Guide 2018]  "Password Storage Cheat Sheet - OWASP", https://web.archive.org/web/20180924221911/https://www.owasp.org/index.php/Password_Storage_Cheat_Sheet#Hash_the_password_as_one_of_several_steps.

## Appendix A. Rationale

- [ ] Possibly add content here about the reasoning for always exactly filling up the $B_{ikm}$ section 100% (ie: no padding) but may not be necessary as it's briefly covered in the section 5 intro  

### A.1. Decimal Encodings Rational

#### A.1.1. Decimal Encoding and Compact Format

Compact format was designed specifically for use with decimal encoding. The goal was to allow two parties to establish mutual authentication by exchanging a short numeric code — something a person can read aloud, hear, and enter on a keypad without difficulty.

To maximize entropy within a small number of digits, Compact format minimizes header overhead, leaving as many bits as possible for IKM.

Voice channels (telephone, video call) are a natural fit for this exchange: they are widely accessible, require no special software, and do not leave a long-lived record of the exchanged message. Transmitting an MTOTP message over a persistent unencrypted channel such as email is discouraged (see Section X).

- [ ] Figure out which section I was intending to link to and update the above "Section X" note (with link).   

Decimal encoding is not the highest-entropy encoding available, and Compact format carries fewer negotiation options than Extended. These are accepted tradeoffs in exchange for simplicity and accessibility.

#### A.1.2. Decimal Encoding: Message Length Derivation

The bit length of a decimal-encoded message is fully determined by the digit count. No out-of-band length field is required. Both Compact (Format bit `0`) and Extended (Format bit `1`) messages are recovered correctly because $B_{message}$ is derived from $N_S$ independently of the integer's magnitude.

#### A.1.3. Decimal Encoding: Floating-Point Arithmetic

The IKM bit length and message bit length formulas for decimal encoding require floating-point evaluation of $\log_{10}(2)$ and $\log_2(10)$. This has been verified to produce correct results for all values within the scope of this specification using IEEE 754 double-precision arithmetic. Implementations SHOULD verify their computed values against the test vectors in [Appendix C.](#appendix-c-test-vectors), which serve as the authoritative reference regardless of floating-point implementation.

### A.2. Key Derivation: Fixed Protocol Salt

RFC 9106 recommends a randomly generated 128-bit salt for Argon2id. MTOTP uses a fixed protocol salt instead. This forces an attacker to build a precomputation table specifically for this protocol rather than reusing existing tables. Per-exchange uniqueness is provided by the IKM entropy.

### A.3. TOTP Parameter Compatibility

The TOTP parameters defined in Section 6.4 (HMAC-SHA-256, 30-second time step, Unix epoch, 6 output digits) were chosen for compatibility with widely deployed TOTP implementations. Fixing these parameters eliminates the need for per-exchange parameter negotiation and removes them from the message format overhead.

### A.4. Difficulty Scale Rational

#### A.4.1. Difficulty Scale Design Goals

The KDF difficulty field provides forward-compatible tuning of key-derivation work within a single protocol version, without consuming additional header bits as hardware improves. It is constrained by the following goals:

1. A single integer expresses difficulty for all supported KDFs.
2. The same integer value across algorithms represents approximately equivalent attacker cost, such that capability advertisement does not need to be per-algorithm.
3. The scale spans from parameters implementable on commodity mobile hardware (2018-era smartphones) through parameters intended for hardware at least one decade beyond publication.
4. Parameters for every level are fully specified in this document; no runtime parameter derivation is performed. Both parties MUST produce identical parameters from identical inputs.

#### A.4.2. Attacker Cost Model

Security is measured in **time-area product (AT)**, the product of the circuit area occupied by a single KDF evaluation and the wall-clock time required for that evaluation on attacker hardware [ARGON2-PAPER].  This is the metric Argon2 was explicitly designed to maximize, and it is the metric used in this document to compare levels across algorithms.

The protocol permits a minimum of 64 bits of shared entropy and does not use a salt. The attacker is therefore assumed to perform keyspace precomputation amortized across all users sharing a given entropy length. A difficulty level MUST be chosen such that the AT cost of computing $2^{64}$ KDF evaluations exceeds any economically rational adversary's budget.

#### A.4.3. Scale Definition

The difficulty field is 3 bits, yielding 8 levels (0 through 7). Each increment of the difficulty field represents approximately a 4x increase in attacker AT cost.  The 4x step was chosen for the following reasons:

1. **It matches scrypt's natural granularity.** scrypt's cost parameter N MUST be a power of 2 [RFC7914](https://www.rfc-editor.org/info/rfc7914).  Each doubling of N doubles both memory and the number of sequential operations over that memory, yielding 4x AT cost per step.  Finer-grained scrypt scaling requires manipulating the r parameter, which departs from the widely-deployed $r=8$
   configuration recommended by [RFC7914](https://www.rfc-editor.org/info/rfc7914) and degrades performance on common implementations due to cache effects.
2. **It aligns with the hardware improvement rate.**  Moore's Law doubles transistor density roughly every 18-24 months. A 4x cost step therefore corresponds to approximately 3-4 years of attacker hardware improvement. An 8-level scale thus covers 24-32 years of projected
   hardware advancement, which allows additional leeway for unforeseen advancement during that period.
3. **It respects the precision of the underlying threat model.** Estimates of future attacker capability (GPU memory bandwidth, ASIC economics, TMTO advances) are uncertain to well more than a factor of 2.

#### A.4.4. Baseline (Level 0)

- [ ] We almost certainly want to lower the baseline / level 0 requirement to avoid preventing people with older devices from using the protocol. This document was written before we started gathering actual device stats. Once we've completed that, this scale will be updated to match.  

Level 0 is calibrated to approximately 3-4x the AT cost of the OWASP 2024 minimum recommendations for Argon2id and scrypt [OWASP-PSCS].  The OWASP minimums are chosen for server-side password verification, where the server processes many concurrent authentications per second and must minimize per-request wall time. This protocol performs KDF evaluation once per pairing (not per authentication code), so a larger per-evaluation cost is acceptable.

Level 0 targets approximately 1 second of wall-clock time on a 2018-era budget smartphone (Cortex-A53-class SoC, LPDDR3/LPDDR4 memory). Implementations running on faster hardware will complete level 0 in proportionally less time.

#### A.4.5. Cross-Algorithm Equivalence

- [ ] Either remove this section or move it to the appendix  

The scale is designed such that the same numeric level across algorithms produces approximately equivalent attacker AT cost.  Equivalence is approximate rather than exact because:

1. The underlying compression functions differ (BLAKE2b for Argon2id, Salsa20/8 for scrypt, HMAC-SHA256 for PBKDF2) and have different constant-factor costs per operation on both defender and attacker hardware.
2. TMTO resistance differs between algorithms.  The nominal AT cost figures above do not account for the ~1.33x reduction achievable against Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106) or the larger reductions achievable against scrypt.
3. PBKDF2 is not memory-hard and provides no ASIC resistance. PBKDF2 level N provides far less effective security than scrypt or Argon2id level N against a well-resourced attacker.

Capability advertisement during pairing specifies a single maximum level applicable to all supported algorithms.  Implementations SHOULD benchmark on first run and set this level to the highest at which every supported algorithm completes within the implementation's time budget.

#### A.4.6. PBKDF2 Historical Iteration Count Trajectory

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

| Year | Recommended iterations | Reference                                                                                                                                                                                                                                                                |
| ---- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2000 | 1,000                  | "For the methods in this document, a minimum of 1000 iterations is recommended." ([RFC2898](https://www.rfc-editor.org/info/rfc2898))                                                                                                                                                                          |
| 2002 | --                     | "Hashing the passwords with a simple hash algorithm like SHA-1 is a commonly used technique." ([OWASP Guide 2002](https://web.archive.org/web/20021021080619/http://www.owasp.org/guide/v11/ch06.html#id2858301))<br>So cute! 😇                                         |
| 2008 | --                     | "Use AES-128 in digest mode or SHA-1 in 256 bit mode" ([OWASP Guide 2008](https://web.archive.org/web/20080914005739/http://www.owasp.org/index.php/Guide_to_Authentication#Best_Practices))                                                                             |
| 2010 | --                     | "The minimum hash strength SHOULD be SHA-256 for the next few years." ([OWASP Guide 2010](https://web.archive.org/web/20100718034930/http://www.owasp.org/index.php/Guide_to_Authentication#Minimum_hash_strength))                                                      |
| 2011 | --                     | "Use a modern hash: SHA or bcrypt" ([OWASP Guide 2011](https://web.archive.org/web/20111008022356/https://www.owasp.org/index.php/Password_Storage_Cheat_Sheet))                                                                                                         |
| 2014 | 10,000                 | "10,000 iterations Apple uses for its iTunes passwords (using PBKDF2)" ([OWASP Guide 2014](https://web.archive.org/web/20140811055758/https://www.owasp.org/index.php/Password_Storage_Cheat_Sheet))                                                                     |
| 2019 | 10,000 - 100,000       | "at least 10,000 (although values of up to 100,000 may be appropriate in higher security environments)." ([OWASP Cheatsheet 2019](https://github.com/OWASP/CheatSheetSeries/blob/2f976f1671c6cb4e9ce9fd8cbb59cf17f31b390e/cheatsheets/Password_Storage_Cheat_Sheet.md))  |
| 2021 | 310,000                | "use PBKDF2 with a work factor of 310,000 or more and set with an internal hash function of HMAC-SHA-256" ([OWASP Cheatsheet 2021](https://github.com/OWASP/CheatSheetSeries/blob/986415b473402de66612dec5cd0b9b896ba6a7c6/cheatsheets/Password_Storage_Cheat_Sheet.md)) |
| 2023 | 600,000                | "use PBKDF2 with a work factor of 600,000 or more and set with an internal hash function of HMAC-SHA-256" ([OWASP Cheatsheet 2023](https://github.com/OWASP/CheatSheetSeries/blob/f14bc4c0578e1328c23094dcb0a1d8e9b778b3ec/cheatsheets/Password_Storage_Cheat_Sheet.md)) |

This represents a ~600x increase over approximately 23 years, or approximately 10 bits of work.  The 4x per-level schedule provides comparable headroom within levels 0-7.

#### A.4.7. Scrypt Difficulty Scaling Rationale

Parameters: $N$ = cost parameter (power of 2 per [RFC7914](https://www.rfc-editor.org/info/rfc7914)), $r = 8$, $p = 1$. The $r=8$, $p=1$ configuration is explicitly recommended in [RFC7914](https://www.rfc-editor.org/info/rfc7914) Section 2 and is the configuration under which scrypt's memory-hardness proofs in [ALWEN-SCRYPT-2016] apply.

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

scrypt's AT cost scales as $N^2$ because each increment of $log_{2}(N)$ doubles both the memory block count and the number of sequential operations over that memory.  Each level therefore corresponds to a single $+1$ step in $log_{2}(N)$, matching the 4x per-level AT target naturally.

Level 0 matches the current OWASP recommended minimum of $N=2^17$, $r=8$, $p=1$ [OWASP-PSCS] scaled down by one $log_{2}(N)$ step.  Level 2 matches the OWASP minimum directly.

#### A.4.8. Scrypt TMTO Resistance

scrypt has been proven maximally memory-hard in the parallel random oracle model [ALWEN-SCRYPT-2016].  However, scrypt is susceptible to certain time-memory tradeoffs not present in Argon2id; specifically, the [ARGON2-PAPER] introduction notes that "the existence of a trivial time-memory tradeoff" in scrypt motivated the development of Argon2. At equivalent nominal AT parameters, Argon2id provides stronger effective resistance to ASIC-based attackers.  For this reason, Argon2id is the preferred algorithm in negotiation; scrypt is retained for implementations that lack a well-optimized Argon2 library.

#### A.4.9. Argon2id Level Calibration

Parameters: $m$ = memory in KiB, $t$ = iterations, $p$ = lanes (per [RFC9106](https://www.rfc-editor.org/info/rfc9106) guidance).  Variant is Argon2id (hybrid), version 0x13.

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

Level 0 matches the [RFC9106](https://www.rfc-editor.org/info/rfc9106) SECOND RECOMMENDED option for memory-constrained environments ($m$=64 MiB, $t$=3, $p$=4), with $t$ reduced to $2$ to bring per-evaluation time closer to 1 second on low-end mobile hardware. Level 2 approximates the [RFC9106](https://www.rfc-editor.org/info/rfc9106) FIRST RECOMMENDED option ($m$=2 GiB, $t$=1) in AT cost terms, and level 5 exceeds it by a factor of approximately 64.

#### A.4.10. Argon2id Historical Parameters Trajectory

| Year | Recommended iterations | Reference                                                                                                                                                                                                                                                                                                                       |
| ---- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2018 | --                     | First mention of Argon2: "Argon2 is the winner of the password hashing competition and should be considered as your first choice for new applications;" ([OWASP Guide 2018](https://web.archive.org/web/20180924221911/https://www.owasp.org/index.php/Password_Storage_Cheat_Sheet#Hash_the_password_as_one_of_several_steps)) |
| 2021 | m=15360, t=2, p=1      | "Use Argon2id with a minimum configuration of 15 MiB of memory, an iteration count of 2, and 1 degree of parallelism" ([OWASP Cheatsheet 2021](https://github.com/OWASP/CheatSheetSeries/blob/986415b473402de66612dec5cd0b9b896ba6a7c6/cheatsheets/Password_Storage_Cheat_Sheet.md))                                            |
| 2023 | m=19456, t=2, p=1      | "Use Argon2id with a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism" ([OWASP Cheatsheet 2023](https://github.com/OWASP/CheatSheetSeries/blob/f14bc4c0578e1328c23094dcb0a1d8e9b778b3ec/cheatsheets/Password_Storage_Cheat_Sheet.md))                                            |

#### A.4.11. Argon2id TMTO Resistance

Argon2id provides strong resistance to time-memory tradeoff (TMTO) attacks. Per [RFC9106](https://www.rfc-editor.org/info/rfc9106) Section 7.2, the best known attack on t-pass Argon2id is the ranking tradeoff attack, reducing the AT product by a factor of 1.33 for $t >= 2$.  At $t=2$ and above, further increases in $t$ do not meaningfully improve TMTO resistance for this range of memory sizes.

However, increasing $t$ beyond 2 remains useful in this protocol because it proportionally increases the attacker's compute requirements at fixed memory. The AT cost scales linearly in $t$ regardless of TMTO resistance. Doubling $t$ per level therefore doubles attacker work independent of memory considerations.

Per [RFC9106](https://www.rfc-editor.org/info/rfc9106), to completely prevent [AB16] time-space tradeoffs, the number of passes MUST exceed $log_{2}($memory_in_blocks$) - 26$.  At $m$=8192 MiB (level 7), this requires $t >= log_{2}(8388608) - 26 = 23 - 26 = -3$, which is trivially satisfied.  At all levels in this table, the [AB16] tradeoff is fully prevented.

- [ ] VERIFY the math / accuracy of this section  

## Appendix B. Examples

### B.1. Decimal Encoding: IKM Bit Length Examples

The following table illustrates the chunking effect of the IKM bit length formula ([Section 4.](#4-mtotp-message-encodings)) for decimal encoding with Compact format overhead ($B_{overhead} = 7$).

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
