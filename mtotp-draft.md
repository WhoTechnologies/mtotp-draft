Who Technologies
Internet-Draft Intended status: Informational

     MTOTP: Mutual Authentication Extension to TOTP
                     draft-mtotp-0.1l

## Abstract

This document describes an extension to the Time-Based One-Time Password (TOTP) algorithm [RFC6238](https://www.rfc-editor.org/info/rfc6238) that enables mutual authentication between two parties.  Standard TOTP provides unidirectional authentication: the verifying party authenticates the code-generating party, but not vice versa.  This document specifies a method by which two parties each contribute Input Keying Material (IKM) to derive two directional TOTP shared secrets, one per direction of verification, without requiring a coordinating server or either party to generate or transmit a complete cryptographic secret


Status of This Memo

This document is not an Internet Standards Track specification.  It is published for informational purposes.

Portions of this specification are subject to a provisional patent application, pending.

## Table of Contents

- [1. Introduction](#1. Introduction)
	- [1.1. Scope](#1.1. Scope)
	- [1.2. Background](#1.2. Background)
- [2. Notation and Terminology](#2. Notation and Terminology)
- [3. MTOTP Message Format](#3. MTOTP Message Format)
	- [3.1. Common Binary Structure](#3.1. Common Binary Structure)
		- [3.1.1. Initial Keying Material (IKM)](#3.1.1. Initial Keying Material (IKM))
		- [3.1.2. Message Checksum](#3.1.2. Message Checksum)
	- [3.2. Extended Format Headers](#3.2. Extended Format Headers)
		- [3.2.1. Extended Format Version Header](#3.2.1. Extended Format Version Header)
		- [3.2.2. Extended v1 Header Structure](#3.2.2. Extended v1 Header Structure)
		- [3.2.3. Extended v1 KDF Algorithm](#3.2.3. Extended v1 KDF Algorithm)
		- [3.2.4. Extended v1 KDF Parameters](#3.2.4. Extended v1 KDF Parameters)
			- [3.2.4.1. PBKDF2 Parameters](#3.2.4.1. PBKDF2 Parameters)
			- [3.2.4.2. Scrypt Parameters](#3.2.4.2. Scrypt Parameters)
			- [3.2.4.3. Argon2id Parameters](#3.2.4.3. Argon2id Parameters)
	- [3.3. Compact Format Headers](#3.3. Compact Format Headers)
		- [3.3.1. Compact Format Binary Structure](#3.3.1. Compact Format Binary Structure)
		- [3.3.2. Compact Format Version](#3.3.2. Compact Format Version)
		- [3.3.3. Compact Format KDF Algorithm](#3.3.3. Compact Format KDF Algorithm)
		- [3.3.4. Compact Format KDF Parameters](#3.3.4. Compact Format KDF Parameters)
			- [3.3.4.1. Compact Format scrypt](#3.3.4.1. Compact Format scrypt)
			- [3.3.4.2. Compact Format Argon2id](#3.3.4.2. Compact Format Argon2id)

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

**M_Alice / M_Bob:**
The MTOTP messages generated by Alice and Bob’s devices.

**IKM_Alice / IKM_Bob:**
The IKM fields of M_Alice and M_Bob.

**Alice:**
The local device and its operator. The roles of Alice and Bob are symmetric; each device considers itself Alice and its peer Bob. The labels are used for expository clarity and do not imply initiation order or protocol asymmetry.

**Bob:**
The remote device and its operator.

**Shared Secrets:**
The TOTP keys derived from the combined IKM values of both parties. Two Shared Secrets are produced per MTOTP message exchange, one per direction of verification. Each Shared Secret serves as the key K in the TOTP computation as defined in [RFC4226](https://www.rfc-editor.org/info/rfc4226) and [RFC6238](https://www.rfc-editor.org/info/rfc6238).

**Password-Based Key Derivation Function (KDF):**
A cryptographic function used to derive a Shared Secret from the combined IKM entropy. Referred in this document as just "KDF" to avoid confusion with the PBKDF2 Algorithm.

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

".." indicates a variable-length field whose size depends on the Message Format bit; see Section [3.2. Extended Format Headers](#3.2. Extended Format Headers) and Section [3.3. Compact Format Headers](#3.3. Compact Format Headers).

**Message Format (1 bit):**
Determines the structure of the Format-Specific Headers field.

| Value | Meaning                           |
| ----- | --------------------------------- |
| `0`   | Extended Format. See Section 4.2. |
| `1`   | Compact Format. See Section 4.3.  |

Compact Format is assigned the value 1 so that the most significant bit of any valid Compact message is always 1, ensuring the binary value is never ambiguous when reconstructed from decimal encoding. See Section [4.1. Decimal Encoding](#4.1. Decimal Encoding).

**Format-Specific Headers (variable):**
Present in all messages.  Structure depends on the value of the Message Format bit. See Sections [3.2. Extended Format Headers](#3.2. Extended Format Headers) and [3.3. Compact Format Headers](#3.3. Compact Format Headers).

**IKM Bits (variable):**
Initial Keying Material. See Section [3.1.1. Initial Keying Material (IKM)](#3.1.1. Initial Keying Material (IKM)).

**Message Checksum (5 bits):**
Occupies the five least significant bits of every MTOTP message. See Section [3.1.2. Message Checksum](#3.1.2. Message Checksum).

#### 3.1.1. Initial Keying Material (IKM)

The IKM field MUST contain a minimum number of bits of entropy generated by a cryptographically secure random source [RFC4086](https://www.rfc-editor.org/info/rfc4086).

> TODO: Confirm minimum IKM entropy in bits.  Current working value: 32 bits per device (64 bits combined) for compact format; 80 bits per device for extended format.  Confirm whether this MUST or SHOULD be enforced, per RFC 6238 and RFC 4226 practice for minimum key lengths. 
> 
> To anyone reading this: Yes, a minimum (the system supports much more, this is minimum only) of 64 bits is not a ton of entropy. This is a usability tradeoff to get people not comfortable with technology to be able to set up a shared secret with another person by entering a short decimal (0-9 only) number, and is why we're doing things like using KDF algorithms to harden the (possibly) low entropy. There will be words to this effect added to the document before publishing.

#### 3.1.2. Message Checksum

The five least significant bits of every MTOTP message are the checksum field. This field is computed identically across all message formats, permitting any implementation to validate the checksum prior to decoding the message content.

The checksum additionally serves a limited domain-separation role. Because MTOTP messages carry no dedicated magic number or protocol identifier, the domain-separated HMAC-SHA256 key "MTOTP-v0" makes the checksum distribution distinct from raw SHA-256 output. This reduces — but does not eliminate — the probability that output from an unrelated system is accepted as a valid MTOTP message.

Let B denote the concatenation of all bits preceding the checksum (i.e., including the format bit, all header bits, and the IKM bits), zero-padded on the right to the nearest byte boundary.  The checksum is computed as:

```
checksum_bits = MSB5(HMAC-SHA256("MTOTP-v0", B))
```

where HMAC-SHA256 is as defined in [RFC4231](https://www.rfc-editor.org/info/rfc4231), MSB5(x) denotes the five most significant bits of the first byte of x, and the HMAC key is the ASCII encoding of the literal string "MTOTP-v0".

Implementations MUST verify the checksum upon decoding an MTOTP message and MUST reject any message that fails verification.

> TODO: Consider whether the checksum length should scale with the IKM length.  Extended format messages carry substantially more entropy than compact format messages; a longer checksum would provide proportionally stronger integrity verification at modest additional overhead cost.

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
| `01`  | Version 1. See Section [3.2.2. Extended v1 Header Structure](#3.2.2. Extended v1 Header Structure). |
| `10`  | Reserved.                                                        |
| `11`  | Reserved.                                                        |
| `00`  | Reserved.                                                        |

Version numbering begins at `01` rather than `00` so that any valid Extended message is guaranteed to contain a `1` bit within the first three bits, ensuring the binary value is never ambiguous when reconstructed from decimal encoding. See Section [4.1. Decimal Encoding](#4.1. Decimal Encoding). Values `00`, `10`, and `11` are reserved for future protocol enhancements or KDF algorithm updates. 

**Version-Specific Headers (variable):**
Structure depends on the Extended Version field.  This document specifies Version 1 only.  See Section [3.2.2. Extended v1 Header Structure](#3.2.2. Extended v1 Header Structure).

A receiver that encounters an Extended Version value it does not recognise or support MUST NOT attempt to parse the remainder of the message, MUST reject the message, and MUST inform the user that the peer device uses an unsupported version of the protocol.

#### 3.2.2. Extended v1 Header Structure

```
Version 01 Headers {
  KDF Algorithm (3 bits),
  KDF Parameters (8 bits),
}
```

**KDF Algorithm (3 bits):**
See Section [3.2.3. Extended v1 KDF Algorithm](#3.2.3. Extended v1 KDF Algorithm).

**KDF Parameters (8 bits):**
See Section [3.2.4. Extended v1 KDF Parameters](#3.2.4. Extended v1 KDF Parameters).

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

| Bit | Value | Algorithm                     |
| --- | ----- | ----------------------------- |
| 1   | `001` | PBKDF2-HMAC-SHA-256 [RFC8018](https://www.rfc-editor.org/info/rfc8018) |
| 2   | `010` | scrypt [RFC7914](https://www.rfc-editor.org/info/rfc7914)              |
| 3   | `100` | Argon2id [RFC9106](https://www.rfc-editor.org/info/rfc9106)            |

The negotiated algorithm is the highest-security algorithm for which both devices have set the corresponding bit. The security ordering from lowest to highest is: PBKDF2-HMAC-SHA-256, scrypt, Argon2id.  If no algorithm bit is set in common by both devices, the exchange MUST fail.

> TODO: Consider adding a section for the above paragraph (ie: "how to choose the common kdf algorithm") instead of embedding it in the header description.

PBKDF2-HMAC-SHA-256 is included solely for environments with FIPS-140 compliance requirements and is considered the weakest of the three supported algorithms. Implementations SHOULD support at least one of scrypt or Argon2id in addition to PBKDF2, ensuring that PBKDF2 is only negotiated when the peer device supports no stronger algorithm. See [3.2.4.1. PBKDF2 Parameters](#3.2.4.1. PBKDF2 Parameters).

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
