Who Technologies
Internet-Draft Intended status: Informational

# MTOTP: Mutual Authentication Extension to TOTP
draft-mtotp-0.1m

## Status of This Memo

This memo provides information for the Internet community. It does not specify an Internet standard of any kind. Distribution of this memo is unlimited.

Portions of this specification are subject to a provisional patent application, pending.

## Copyright Notice

Copyright (C) Who Technologies (2026).

## Abstract

This document describes an extension to the Time-Based One-Time Password (TOTP) algorithm [RFC6238](https://www.rfc-editor.org/info/rfc6238) that enables mutual authentication between two parties.  Standard TOTP provides unidirectional authentication: the verifying party authenticates the code-generating party, but not vice versa.  This document specifies a method by which two parties each contribute Input Keying Material (IKM) to derive two directional TOTP shared secrets, one per direction of verification, without requiring a coordinating server or either party to generate or transmit a complete cryptographic secret.

## Table of Contents

- 1. Introduction
	- 1.1. Scope
	- 1.2. Background
- 2. Notation and Terminology
- 3. MTOTP Message Format
	- 3.1. Common Binary Structure
		- 3.1.1. Initial Keying Material (IKM)
		- 3.1.2. Message Checksum
	- 3.2. Extended Format Headers
		- 3.2.1. Extended Format Version Header
		- 3.2.2. Extended v1 Header Structure
		- 3.2.3. Extended v1 KDF Algorithm
		- 3.2.4. Extended v1 KDF Parameters
			- 3.2.4.1. PBKDF2 Parameters
			- 3.2.4.2. Scrypt Parameters
			- 3.2.4.3. Argon2id Parameters
	- 3.3. Compact Format Headers
		- 3.3.1. Compact Format Binary Structure
		- 3.3.2. Compact Format Version
		- 3.3.3. Compact Format KDF Algorithm
		- 3.3.4. Compact Format KDF Parameters
			- 3.3.4.1. Compact Format scrypt
			- 3.3.4.2. Compact Format Argon2id
- 4. MTOTP Message Encodings
	- 4.1. Decimal Encoding
		- 4.1.1. Calculate the IKM Bit Length
		- 4.1.2. Calculate Decimal Length from Bit Length
		- 4.1.3. Calculate Message Bit Length from Decimal Length
		- 4.1.4. Decimal Encode Procedure
		- 4.1.5. Decimal Decode Procedure
	- 4.2. BIP39 Word List Encoding
		- 4.2.1. Section 4.2.1 Calculate the IKM Bit Length
		- 4.2.2. Section 4.2.2 Calculate Word Count from Bit Length
		- 4.2.3. Section 4.2.4 BIP39 Encode Procedure
		- 4.2.4. Section 4.2.5 BIP39 Decode Procedure
	- 4.3. Encoded String
		- 4.3.1. Section 4.3.1 Calculate the IKM Bit Length
		- 4.3.2. Section 4.3.2 Base64URL Encode Procedure
		- 4.3.3. Section 4.3.3 Base64URL Decode Procedure
	- 4.4. JSON Format
- 5. Secret Derivation
	- 5.1. IKM Identification
	- 5.2. Pre-Derivation Hash
	- 5.3. Password-Based Key Derivation Function
	- 5.4. Directional Assignment
	- 5.5. TOTP Application
- 6. Clock Synchronization

## 1. Introduction

### 1.1. Scope

This document specifies MTOTP, an extension to TOTP [RFC6238](https://www.rfc-editor.org/info/rfc6238) that enables mutual authentication. 

Specifically, this document defines:

- A binary format for MTOTP messages in two versions: a compact version suitable for numerical entry using fixed KDF parameters; and an advanced version carrying explicit negotiated KDF algorithm and parameters;
- Encoding formats for exchanging MTOTP messages over voice, text, and digital channels;
- A key derivation procedure that produces two directional TOTP shared secrets from the IKM values of both parties; and
- Normative TOTP parameters for use with the derived secrets.

Provisioning flows, user interface behavior, contact management, and clock synchronization beyond are outside the scope of this document.

### 1.2. Background

As defined in [RFC6238](https://www.rfc-editor.org/info/rfc6238), TOTP requires a shared secret established at provisioning time.  The verifying party authenticates the code-generating party; the authentication relationship is unidirectional.

Section 9 of [RFC4226](https://www.rfc-editor.org/info/rfc4226) describes a three-pass mutual authentication scheme using HOTP, in which the client presents a first one-time password, the server responds with a second, and the client verifies the server response. The TOTP equivalent requires one party to defer code presentation until the following 30-second time window, a constraint that is impractical for real-time human-to-human interaction.

MTOTP addresses this by deriving two directional secrets from a pair of independently generated IKM values, one contributed by each party.  The derivation uses the two IKM values in opposite concatenation orderings, such that both devices independently arrive at identical results. Alice’s outbound shared secret equals Bob’s inbound shared secret, and vice versa, without additional coordination after the initial MTOTP message exchange.

In addition, where standard TOTP provisioning relies on the `otpauth://` URI scheme transmitted via QR code or copy-paste, the exchange of the parameters and IKM values can be encoded into a single number or phrase that humans can comfortably read, convey, and transcribe. This makes the provisioning exchange viable over voice or other low-bandwidth channels where QR codes and digital copy-paste are unavailable.

## 2. Notation and Terminology

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “NOT RECOMMENDED”, “MAY”, and “OPTIONAL” in this document are to be interpreted as described in [RFC2119](https://www.rfc-editor.org/info/rfc2119) when, and only when, they appear in all capitals, as shown here.

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

> TODO: Add symbols? https://www.ietf.org/rfc/rfc4226.txt

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

`..` indicates a variable-length field whose size depends on the Message Format bit.

**Message Format (1 bit):**
Determines the structure of the Format-Specific Headers field.

| Value | Meaning                                                         |
| ----- | --------------------------------------------------------------- |
| `0`   | Extended Format. See Section [[#3.2. Extended Format Headers]]. |
| `1`   | Compact Format. See Section [[#3.3. Compact Format Headers]].   |

**Format-Specific Headers (variable):**
Present in all messages.  Structure depends on the value of the Message Format bit. See Sections [[#3.2. Extended Format Headers]] and [[#3.3. Compact Format Headers]].

**IKM Bits (variable):**
Initial Keying Material. See Section [[#3.1.1. Initial Keying Material (IKM)]].

**Message Checksum (5 bits):**
Occupies the five least significant bits of every MTOTP message. See Section [[#3.1.2. Message Checksum]].

#### 3.1.1. Initial Keying Material (IKM)

The IKM field MUST contain a minimum number of bits of entropy generated by a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086). 

IKM length is not a completely free parameter — it is determined by the choice of encoding, message format, and encoding length. The IKM field occupies all remaining bits after the headers and checksum for the message format in use.

Each encoding has a natural granularity: a minimum bit size and step size that the total message length must be a multiple of. For example, BIP39 words each represent 11 bits, so valid message lengths are 11, 22, 33, 44 bits and so on — no intermediate lengths are possible. Once an encoding is chosen, implementations MUST use the maximum IKM length that fits within the encoding's natural granularity, and MUST NOT transmit fewer bits of entropy than the encoding can carry. Doing so would reduce the entropy of the exchange without reducing its size.

Formulas to calculate the encoding granularity for each supported encoding, along with examples, are defined in Section 5.

The minimum combined IKM entropy for an exchange is 64 bits (32 bits per device). Implementations MUST verify the combined IKM length and MUST reject any message that would result in less than 64 bits of combined IKM entropy.

**Note (Non-Normative):** A minimum combined entropy of 64 bits is intentionally low by cryptographic standards. This reflects a deliberate usability tradeoff for one specific use case of MTOTP: allowing users who are not technically sophisticated to establish a shared secret by exchanging a short numeric string. MTOTP is fully capable of carrying much higher entropy — longer codes, BIP39 words, or Base64URL strings are strongly encouraged where usability permits. The KDF step is specifically chosen and parameterised to harden low-entropy inputs against brute-force attack.

#### 3.1.2. Message Checksum

The five least significant bits of every MTOTP message are the checksum field. This field is computed identically across all message formats, permitting any implementation to validate the checksum prior to decoding the message content.

The checksum additionally serves a limited domain-separation role. Because MTOTP messages carry no dedicated magic number or protocol identifier, the domain-separated HMAC-SHA256 key "MTOTP-v0" makes the checksum distribution distinct from raw SHA-256 output. This reduces — but does not eliminate — the probability that output from an unrelated system is accepted as a valid MTOTP message.

Let B denote the concatenation of all bits preceding the checksum (i.e., including the format bit, all header bits, and the IKM bits), zero-padded on the right to the nearest byte boundary.  The checksum is computed as:

```
checksum_bits = MSB5(HMAC-SHA256("MTOTP-v0", B))
```

where HMAC-SHA256 is as defined in [RFC4231](https://www.rfc-editor.org/info/rfc4231), MSB5(x) denotes the five most significant bits of the first byte of x, and the HMAC key is the ASCII encoding of the literal string "MTOTP-v0".

Implementations MUST verify the checksum upon decoding an MTOTP message and MUST reject any message that fails verification.

> **TODO:** Consider whether the checksum length should scale with message length. Longer messages provide more opportunity for transcription error; a longer checksum would provide proportionally stronger error detection at the cost of one bit of IKM entropy per additional checksum bit.

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
| `01`  | Version 1. See Section [[#3.2.2. Extended v1 Header Structure]]. |
| `10`  | Reserved.                                                        |
| `11`  | Reserved.                                                        |
| `00`  | Reserved.                                                        |

Version numbering begins at `01` rather than `00` so that any valid Extended message is guaranteed to contain a `1` bit within the first three bits, ensuring the binary value is never ambiguous when reconstructed from decimal encoding. See Section [[#4.1. Decimal Encoding]]. Values `00`, `10`, and `11` are reserved for future protocol enhancements or KDF algorithm updates. 

**Version-Specific Headers (variable):**
Structure depends on the Extended Version field.  This document specifies Version 1 only.  See Section [[#3.2.2. Extended v1 Header Structure]].

A receiver that encounters an Extended Version value it does not recognise or support MUST NOT attempt to parse the remainder of the message, MUST reject the message, and MUST inform the user that the peer device uses an unsupported version of the protocol.

#### 3.2.2. Extended v1 Header Structure

```
Version 01 Headers {
  KDF Algorithm (3 bits),
  KDF Parameters (8 bits),
}
```

**KDF Algorithm (3 bits):**
See Section [[#3.2.3. Extended v1 KDF Algorithm]].

**KDF Parameters (8 bits):**
See Section [[#3.2.4. Extended v1 KDF Parameters]].

> TODO: Note the number of bits required for the KDF Parameters is subject to change as we finalize the KDF Parameters section.

**The total message overhead for Extended Format Version 1 is 19 bits:**

| Field            | Bits   |
| ---------------- | ------ |
| Message Format   | 1      |
| Extended Version | 2      |
| KDF Algorithm    | 3      |
| KDF Parameters   | 8      |
| Message Checksum | 5      |
| **Total**        | **19** |

#### 3.2.3. Extended v1 KDF Algorithm

Each bit in the KDF Algorithm field indicates support for one algorithm. A device MUST set each bit corresponding to an algorithm it supports. More than one bit MAY be set.

| Value | Algorithm                                                              |
| ----- | ---------------------------------------------------------------------- |
| `001` | PBKDF2-HMAC-SHA-256 [RFC8018](https://www.rfc-editor.org/info/rfc8018) |
| `010` | scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914)              |
| `100` | Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106)            |

The negotiated algorithm is the highest-security algorithm for which both devices have set the corresponding bit. The security ordering from lowest to highest is: PBKDF2-HMAC-SHA-256, scrypt, Argon2id.  If no algorithm bit is set in common by both devices, the exchange MUST fail.

> TODO: Consider adding a section for the above paragraph (ie: "how to choose the common kdf algorithm") instead of embedding it in the header description.

PBKDF2-HMAC-SHA-256 is included solely for environments with FIPS-140 compliance requirements and is considered the weakest of the three supported algorithms. Implementations SHOULD support at least one of scrypt or Argon2id in addition to PBKDF2, ensuring that PBKDF2 is only negotiated when the peer device supports no stronger algorithm. See [[#3.2.4.1. PBKDF2 Parameters]].

#### 3.2.4. Extended v1 KDF Parameters

> TODO: We either need to provide parameters for all algorithms (ugly) or provide a global difficulty level that maps to specific parameters for each algorithm, roughly equivalent in terms of the load required by the device / security level. 

 > TODO: Define a unified difficulty parameter that maps a single index value to a complete set of algorithm parameters, independent of which algorithm is selected.  This would simplify the Parameters field and allow implementations to express security level without per-algorithm knowledge. Each device would set the maximum difficulty level they can reasonably support (ie taking into account certain memory and cpu limitations) and then the devices would both use the lowest setting.
 
If the specified difficulty level and entropy combined would create a secret too weak to provide proper security, the exchange MUST fail. 

> TODO: define this very nebulous concept. The biggest risk being PBKDF, which is why it’s banned from compact mode which is designed for smaller amounts of entropy. 
 
##### 3.2.4.1. PBKDF2 Parameters

> TODO: Define the PBKDF2 iterations table.  OWASP minimum is 600,000 iterations [OWASP].  This should be the minimum, and we should allow increases beyond that so that the protocol can extend as cracking gets faster.
> 
> A non-linear scale is preferred over simple doubling to avoid excessively large jumps at higher values. Simplest would just be to treat it as an int and multiply it by 100,000 to get the number of iterations. 

> TODO: Confirm whether a minimum combined IKM entropy level should be required when PBKDF2 is negotiated, and if so what that minimum should be.

##### 3.2.4.2. Scrypt Parameters

> TODO: Define the scrypt memory level table.  OWASP recommendation is a minimum CPU/memory cost parameter of (2^17), a minimum block size of 8 (1024 bytes), and a parallelization parameter of 1. 
> 
> This should be the minimum, and we should allow increases beyond that so that the protocol can extend as cracking gets faster.
> 
> OWASP Recommends:
> 
> Scrypt has three parameters that can be configured: the minimum memory cost parameter (N), the blocksize (r), and the degree of parallelism (p). Use one of the following settings:
> 
> - N=2^17 (128 MiB), r=8 (1024 bytes), p=1
> - N=2^16 (64 MiB), r=8 (1024 bytes), p=2
> - N=2^15 (32 MiB), r=8 (1024 bytes), p=3
> - N=2^14 (16 MiB), r=8 (1024 bytes), p=5
> - N=2^13 (8 MiB), r=8 (1024 bytes), p=10

##### 3.2.4.3. Argon2id Parameters

> TODO: Define the Argon2id memory level table.  OWASP recommendation is a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism.
> 
> This should be the minimum, and we should allow increases beyond that so that the protocol can extend as cracking gets faster.
> 
> OWASP Recommends:
> 
> These parameters control how computationally expensive it is to compute a password hash. Increasing memory usage, iteration count, or parallelism makes password cracking attempts significantly slower and more costly for attackers, while still remaining practical for legitimate authentication requests when tuned appropriately.
> - m=47104 (46 MiB), t=1, p=1 (Do not use with Argon2i)
> - m=19456 (19 MiB), t=2, p=1 (Do not use with Argon2i)
> - m=12288 (12 MiB), t=3, p=1
> - m=9216 (9 MiB), t=4, p=1
> - m=7168 (7 MiB), t=5, p=1
> These configuration settings provide an equal level of defense, and the only difference is a trade off between CPU and RAM usage.
> 
> ...but we want increasing difficulty, so we should support the recommended, and then harder versions (not just trading off memory for cpu).

### 3.3. Compact Format Headers

The Compact Format trades configurability for minimal overhead, using fixed KDF parameters to preserve as many bits as possible for entropy. It is intended for constrained exchange channels and for users who are uncomfortable with phrase-based entry, preferring to enter a short numeric string on a keypad rather than a word list or encoded string. This is an explicit usability tradeoff: the reduced overhead provides enough security for casual or non-mission-critical use cases, but implementations SHOULD prefer Extended Format where the exchange channel and user comfort permit.

With a 32-bit IKM, the total message length — comprising all header fields, the IKM, and the 5-bit checksum — is 39 bits, giving a maximum decimal value of 2^39 - 1 = 549,755,813,887, which fits within 12 decimal digits.

#### 3.3.1. Compact Format Binary Structure

```
Compact Format Headers {
  KDF Algorithm (1 bit),
}
```

The total message overhead for Compact Format is 7 bits:

| Field               | Bits |
|---------------------|------|
| Message Format      | 1    |
| KDF Algorithm       | 1    |
| Message Checksum    | 5    |
| **Total**           | **7** |

#### 3.3.2. Compact Format Version

The Compact Format contains no version field. Version omission is intentional; the saved bits are allocated to entropy.

#### 3.3.3. Compact Format KDF Algorithm

The Compact Format uses a single bit to indicate the highest-security algorithm the device supports. An implementation MUST support scrypt in order to support Compact Format; scrypt is the baseline and cannot be omitted.

| Value | scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914) | Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106) |
|-------|------------------|--------------------|
| `0`   | Supported        | Not supported      |
| `1`   | Supported        | Supported          |

A device that sets this bit to `1` implicitly supports scrypt as a fallback, ensuring that negotiation succeeds with any compliant peer.

PBKDF2-HMAC-SHA-256 is explicitly prohibited in Compact Format. Compact Format provides less entropy than Extended Format by design, and PBKDF2 is insufficiently resistant to brute-force attacks against low-entropy sources. An implementation MUST NOT negotiate PBKDF2 in Compact Format under any circumstances, including interoperability with a peer that does not support scrypt or Argon2id. In such cases, the exchange MUST fail.

#### 3.3.4. Compact Format KDF Parameters

To conserve space and account for the reduced entropy available in Compact Format, KDF parameters are fixed rather than negotiated. Parameters are chosen conservatively, following current OWASP recommendations. 

> TODO: "fixed to OWASP recommendations" is load-bearing text here — confirm specific parameter values before this document advances. Also consider whether a 1- or 2-bit difficulty hint is feasible within the overhead budget; see TODOs in 4.3.4.1 and 4.3.4.2.
> 
> This is famous last words all rolled up into one little section right here. 😭

##### 3.3.4.1. Compact Format scrypt

> TODO: Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...?

##### 3.3.4.2. Compact Format Argon2id

>  TODO: Decide on parameters, would be REALLY nice to have that "difficulty" field from the extended format, if we could squeeze a bit or two extra out by using Hex instead of Decimal for example...?

## 4. MTOTP Message Encodings

The binary MTOTP message is the normative form; the encodings defined in this section are representations of that binary value that are more easily transmitted by humans.

For all encodings, implementations MUST calculate and use the maximum IKM length that fits within the encoding's natural capacity (see "Calculate the IKM Bit Length" in each Encoding section). Encoding a message with fewer IKM bits than the encoding can carry wastes entropy, disguises the security of the IKM, and makes decoding ambiguous. 

Since the IKM requires at least 64 bits of entropy (see Section [[#3.1.1. Initial Keying Material (IKM)]]), implementations MUST NOT generate encoding and format combination containing less than 32 bits of IKM (half the required amount).

> TODO: Reword above paragraphs.

### 4.1. Decimal Encoding

The decimal encoding represents an MTOTP message as a decimal digit string, suitable for spoken exchange over a voice channel or manual entry on a numeric keypad. Formatting characters such as spaces or hyphens MAY be added by the implementation for readability and MUST be stripped before decoding.

Because Extended Format requires 12 additional bits of overhead compared to Compact, and because decimal encoding's limited capacity makes those overhead bits costly, decimal encoding is not recommended for Extended Format messages. Extended Format is better suited to encodings with higher natural capacity such as BIP39 or Base64.

> TODO: Reword the above to be the other way around. ie: Compact format was specifically designed for decimal digits, and extended could be used but is not recommended.

> TODO: Add implementation note that while the UI can format digits in a specific way while the user is entering them (ie: expending 12 digits in groups of 3), the UI MUST allow the user to enter any number of digits, to allow for communication with implementations with differing numbers of digits...

#### 4.1.1. Calculate the IKM Bit Length

Given a desired minimum IKM bit length of $B_{min}$ and the Format overhead $B_{overhead}$ (7 bits for Compact, 19 for Extended), calculate the actual IKM bit length required $B_{ikm}$:

$$B_{ikm} = \lfloor \lceil ( B_{overhead} + B_{min} ) \times \log_{10}(2) \rceil \times \log_{2}(10) \rfloor - B_{overhead}$$

This ensures that $D$ decimal digits can represent exactly the total message bit length ($B_{overhead} + B_{ikm}$), with no unused capacity. A message one bit longer would require an additional digit.

Compact format (overhead = 7 bits) examples (notice the "chunking" effect):

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

> **Implementation Note (Non-Normative):** The formulas involve floating-point evaluation of $\log_{10}(2)$ and $\log_{2}(10)$. This has been verified to produce correct results for all values within the scope of this specification using IEEE 754 double-precision arithmetic. Implementations SHOULD verify their computed values against the test vectors in Appendix X, which serve as the authoritative reference regardless of floating-point implementation.

> TODO: Add appendix and consider changing this to an exact calculation instead of using floating point. Even though it's probably fine, I hate the uncertainty of it.

#### 4.1.2. Calculate Decimal Length from Bit Length

Given a calculated $B_{ikm}$ and the Format overhead $B_{overhead}$ (7 bits for Compact, 19 for Extended), calculate the number of decimal digits required $D$:

$$D = \lceil ( B_{overhead} + B_{ikm} ) \times \log_{10}(2) \rceil$$

Compact format (overhead = 7 bits) examples:

| $B_{overhead}$ | $B_{ikm}$ | $B_{overhead}+B_{ikm}$ | Calculated $D$ |
| -------------- | --------- | ---------------------- | -------------- |
| 7              | 32        | 39                     | 12             |
| 7              | 36        | 43                     | 13             |
| 7              | 39        | 46                     | 14             |
| 7              | 42        | 49                     | 15             |
| ...etc         |           |                        |                |

> **Implementation Note (Non-Normative):** See the note in Section 5.1.1 regarding floating-point evaluation of logarithm formulas.

#### 4.1.3. Calculate Message Bit Length from Decimal Length

Given an input length of $D$ digits, calculate the message length in bits $B_{message}$:

$$B_{message} = \lfloor D \times \log_{2}(10) \rfloor$$

Examples:

| $D$    | Calculated $B_{message}$ |
| ------ | ------------------------ |
| 12     | 39                       |
| 13     | 43                       |
| 14     | 46                       |
| 15     | 49                       |
| ...etc |                          |

> **Implementation Note (Non-Normative):** See the note in Section 5.1.1 regarding floating-point evaluation of logarithm formulas.

#### 4.1.4. Decimal Encode Procedure

An implementation SHALL encode an MTOTP binary message to a decimal string as follows:

1. Determine the format (Compact or Extended) and minimum desired IKM entropy $B_{min}$.
2. Calculate the required IKM Bit Length $B_{ikm}$ per Section [[#4.1.1. Calculate the IKM Bit Length]].
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source RFC4086.
4. Construct the complete MTOTP binary message per Section [[#3. MTOTP Message Format]].
5. Calculate the Decimal Length $D$ per Section [[#4.1.2. Calculate Decimal Length from Bit Length]].
6. Interpret the binary message as a single non-negative integer in big-endian byte order, where the first byte is the most significant. Within each byte, bit 7 is the most significant bit. Implementations MUST use arbitrary-precision unsigned integer arithmetic and MUST NOT use fixed-width integer types (e.g., uint64) as an intermediate representation.
7. 1. Express the integer as a decimal digit string, left-padded with zeros to exactly $D$ digits. The resulting string MUST contain exactly $D$ characters, each in the range `0`-`9`.

Leading zeros are significant and MUST be preserved. Omitting them would alter the binary value they represent.

#### 4.1.5. Decimal Decode Procedure

An implementation SHALL decode an MTOTP decimal string to a binary message as follows:

1. Strip all formatting characters from the input string. Any character outside the range `0`-`9` (including spaces, hyphens, and grouping separators) MUST be removed before processing.
2. Count the remaining decimal digits to obtain $D$. 
3. Calculate the message bit length $B_{message}$ per Section [[#4.1.3. Calculate Message Bit Length from Decimal Length]].
4. Parse the decimal string as a single non-negative integer using arbitrary-precision unsigned integer arithmetic. Implementations MUST NOT use fixed-width integer types (e.g., uint64) as an intermediate representation.
5. If the parsed integer requires more bits than $B_{message}$ to represent, the message is malformed and the implementation MUST reject it with an error.
6. Serialize the integer to exactly $B = \lceil B_{message} / 8 \rceil$ bytes in big-endian order, zero-padded on the left. This is the MTOTP binary message.
7. Validate and decode the MTOTP binary message per Section [[#3. MTOTP Message Format]].

The bit length is fully determined by the digit count $D$, so no out-of-band length field is required. A Compact message whose Format bit is `0` and an Extended message whose Format bit is `1` are both recovered exactly because $B_{message}$ is derived independently of the integer's magnitude.

### 4.2. BIP39 Word List Encoding

The BIP39 word list encoding represents an MTOTP message as a sequence of words drawn from the BIP39 word list [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki), suitable for spoken or text-based exchange.  The BIP39 word list contains 2048 entries, such that each word encodes exactly 11 bits.

Note: This encoding uses the BIP39 word list as an encoding alphabet only.  It does not follow the full BIP39 standard BIP39, which mandates specific input lengths and appends its own checksum bits.  Implementations MUST NOT apply or verify a BIP39 checksum when using this encoding; integrity is provided solely by the MTOTP checksum (Section [[#3.1.2. Message Checksum]]).

#### 4.2.1. Section 4.2.1 Calculate the IKM Bit Length

Given a desired minimum IKM bit length $B_{min}$ and the format overhead $B_{overhead}$  (7 bits for Compact, 19 for Extended), calculate the required IKM bit length $B_{ikm}$:

$$B_{ikm} = \left\lceil \frac{B_{overhead} + B_{min}}{11} \right\rceil \times 11 - B_{overhead}$$​

This ensures the total message length ($B_{overhead} + B_{ikm}$) is always an exact multiple of 11, so that the encoded message fills a whole number of words with no padding required.

Extended format (overhead = 19 bits) examples:

| $B_{overhead}$ | $B_{min}$​ | $B_{ikm}$​ |
| -------------- | ---------- | ---------- |
| 19             | 40         | 47         |
| 19             | 41         | 47         |
| ...            | ...        | ...        |
| 19             | 46         | 47         |
| 19             | 47         | 47         |
| 19             | 48         | 58         |
| 19             | 49         | 58         |
| ...            | ...        | ...        |
| 19             | 57         | 58         |
| 19             | 58         | 58         |
| 19             | 59         | 69         |
| ...etc         |            |            |

#### 4.2.2. Section 4.2.2 Calculate Word Count from Bit Length

Given $B_{ikm}$ and $B_{overhead}$, calculate the number of words $W$:

$$W = \frac{B_{overhead} + B_{ikm}}{11}$$

This is exact integer division. Section [[#Section 4.2.1 — Calculate the IKM Bit Length]] guarantees $(B_{overhead} + B_{ikm})$ is always a multiple of 11, so $W$ is always a whole number.

Extended format (overhead = 19 bits) examples:

| $B_{overhead}$ | $B_{ikm}$ | $B_{overhead}+B_{ikm}$ | $W$ |
| -------------- | --------- | ---------------------- | --- |
| 19             | 47        | 66                     | 6   |
| 19             | 58        | 77                     | 7   |
| 19             | 69        | 88                     | 8   |
| 19             | 80        | 99                     | 9   |

#### 4.2.3. Section 4.2.4 BIP39 Encode Procedure

An implementation SHALL encode an MTOTP binary message to a BIP39 word sequence as follows:

1. Determine the format (Compact or Extended) and the minimum desired IKM entropy $B_{min}$.
2. Calculate the required IKM bit length $B_{ikm}$ per Section [[#Section 4.2.1 — Calculate the IKM Bit Length]].
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source RFC4086.
4. Construct the complete MTOTP binary message per Section [[#3. MTOTP Message Format]].
5. Read the message bits from most significant to least significant, taking 11 bits at a time.
6. For each 11-bit group, interpret it as an unsigned integer in the range 0–2047 and select the corresponding entry from the BIP39 word list. The resulting sequence of words is the encoded message.

#### 4.2.4. Section 4.2.5 BIP39 Decode Procedure

An implementation SHALL decode a BIP39 word sequence to an MTOTP binary message as follows:

1. For each word in the input sequence, locate its index in the BIP39 word list. If any word is not found in the word list, the message is malformed and the implementation MUST reject it with an error.
2. Concatenate the 11-bit binary representations of the word indices, from first word to last. The resulting bit string is the MTOTP binary message.
3. Validate and decode the MTOTP binary message per Section [[#3. MTOTP Message Format]].

### 4.3. Encoded String

The encoded string format represents an MTOTP message as a Base64URL-encoded string, suitable for copy-paste over secure digital channels including encrypted chat, and for use as a URI or app intent.

Format:
```
MTOTP;base64url,<data>
```

`<data>` is the MTOTP binary message encoded as Base64URL per [RFC4648](https://www.rfc-editor.org/info/rfc4648) Section 5.

The prefix `MTOTP;base64url,` is case-sensitive. Decoders MUST reject strings that do not conform to this format.

An encoded string MAY be represented as a QR code using any conformant QR code encoder for in-person or camera-based exchange. No additional specification is required for QR encoding.

#### 4.3.1. Section 4.3.1 Calculate the IKM Bit Length

Given a desired minimum IKM bit length $B_{min}$ and the format overhead $B_{overhead}$ (7 bits for Compact, 19 for Extended), calculate the required IKM bit length $B_{ikm}$:

$$B_{ikm} = \left\lceil \frac{B_{overhead} + B_{min}}{6} \right\rceil \times 6 - B_{overhead}$$

This ensures the total message length $(B_{overhead} + B_{ikm})$ is always an exact multiple of 6, so that the encoded message fills a whole number of Base64URL characters with no padding required.

Compact format (overhead = 7 bits) examples:

| $B_{overhead}$ | $B_{min}$ | $B_{ikm}$ |
| -------------- | --------- | --------- |
| 19             | 64        | 65        |
| 19             | 65        | 65        |
| 19             | 66        | 71        |
| 19             | 67        | 71        |
| 19             | 68        | 71        |
| 19             | 69        | 71        |
| 19             | 70        | 71        |
| 19             | 71        | 71        |
| 19             | 72        | 77        |
| ...etc         |           |           |

#### 4.3.2. Section 4.3.2 Base64URL Encode Procedure

An implementation SHALL encode an MTOTP binary message to a Base64URL string as follows:

1. Determine the format (Compact or Extended) and the minimum desired IKM entropy $B_{min}$.
2. Calculate the required IKM bit length $B_{ikm}$ per Section [[#Section 4.3.1 — Calculate the IKM Bit Length]].
3. Generate exactly $B_{ikm}$ bits of IKM from a cryptographically secure random source RFC4086.
4. Construct the complete MTOTP binary message per Section [[#3. MTOTP Message Format]].
5. Encode the binary message as Base64URL per RFC4648 Section 5.
6. Prepend the ASCII prefix `MTOTP;base64url,` to produce the encoded string.

An encoded string MAY be represented as a QR code using any conformant QR code encoder for in-person or camera-based exchange. No additional specification is required for QR encoding.

#### 4.3.3. Section 4.3.3 Base64URL Decode Procedure

An implementation SHALL decode a Base64URL encoded string to an MTOTP binary message as follows:

1. Verify the string begins with the the ASCII prefix `MTOTP;base64url,`. If not, the message is malformed and the implementation MUST reject it with an error.
2. Strip the prefix to obtain the Base64URL encoded data.
3. Decode the Base64URL data per RFC4648 Section 5. The resulting bit string is the MTOTP binary message.
4. Validate and decode the MTOTP binary message per Section [[#3. MTOTP Message Format]].

### 4.4. JSON Format

> TODO: Maybe? Maybe unnecessary due to the compact string encoding.  Define JSON schema and field names.

## 5. Secret Derivation

### 5.1. IKM Identification

Both MTOTP messages MUST be exchanged and decoded per Section [[#4. MTOTP Message Encodings]] before derivation begins. The IKM field of each decoded message is identified per the binary structure defined in Section [[#3.1. Common Binary Structure]].

Let:
IKM_Alice = the IKM field of M_Alice
IKM_Bob   = the IKM field of M_Bob

Only the IKM fields are used as inputs to the derivation.  The header and checksum fields do not contribute to the entropy of the derived secrets.

### 5.2. Pre-Derivation Hash

Two 256-bit intermediate values are computed by applying SHA-256 to the IKM fields concatenated in opposite orderings:

```
  H_out = SHA-256(IKM_Alice || IKM_Bob)
  H_in  = SHA-256(IKM_Bob   || IKM_Alice)
```

The pre-derivation hash applies SHA-256 to both orderings of the IKM fields. This ensures that even low-entropy IKM values are distributed across the full 256-bit output space, increasing the cost of precomputation attacks. It does not increase the entropy of the IKM inputs.

### 5.3. Password-Based Key Derivation Function

The KDF algorithm and parameters are determined by the message format, as follows.

The protocol salt “MTOTP-v0” is a fixed ASCII string used by all KDF invocations in both formats.  It is not secret and does not contribute entropy.  It provides domain separation from other uses of the same KDF functions and distinguishes this protocol version from future revisions.

**Note:** RFC 9106 recommends a randomly generated 128-bit salt for Argon2id. MTOTP uses a fixed protocol salt instead. This forces an attacker to build a precomputation table specifically for this protocol rather than reusing existing tables. Per-exchange uniqueness is provided by the IKM entropy.

Two Shared Secrets are derived:

```
  SharedSecret_out = KDF(H_out, salt="MTOTP-v0", <parameters>)
  SharedSecret_in  = KDF(H_in,  salt="MTOTP-v0", <parameters>)
```

KDF computation occurs once per contact establishment, not per authentication event.

### 5.4. Directional Assignment

From Alice’s perspective, the derived secrets are assigned as follows:

```
SharedSecret_out:  Alice uses this secret as TOTP key K to generate codes she presents to Bob.

SharedSecret_in:   Alice uses this secret as TOTP key K to verify codes that Bob presents to her.
```

The same calculation is performed by both parties. When Bob derives his keys, he simply swaps the labels — his own IKM is $KM_{Alice}$ and Alice's IKM is $IKM_{Bob}$​. The result is that both parties independently arrive at matching directional keys without any additional coordination.

### 5.5. TOTP Application

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

## 6. Clock Synchronization

Correct TOTP operation requires that both devices maintain accurate Unix time.  Implementations SHOULD follow the clock synchronization and resynchronization guidance in [RFC6238](https://www.rfc-editor.org/info/rfc6238), including acceptance of codes from adjacent time steps.
