# Artifact Verification Instructions

These instructions are intentionally non-technical and require no proprietary tools.

This delivery includes cryptographic hashes to make the artifacts **tamper-evident**.

These hashes allow any third party to independently verify that the files have not been altered since delivery.

## What This Verifies

* That the files you received are **bit-for-bit identical** to the files delivered.
* That no content has been modified, replaced, or edited after delivery.

This does **not** certify correctness, compliance, or legal sufficiency.
It certifies **integrity**.

---

## Files Covered

All PDF artifacts and the accompanying README are included in the integrity check.

A list of filenames and their SHA-256 hashes is provided in the **Artifact Integrity** section of the README.

---

## How to Verify (macOS / Linux)

1. Open a terminal.
2. Navigate to the delivery directory.
3. Run:

```
sha256sum <filename>
```

Example:

```
sha256sum Executive_Summary.pdf
```

4. Compare the output to the hash listed in the README.

If the values match exactly, the file is verified.

---

## How to Verify (Windows)

1. Open PowerShell.
2. Navigate to the delivery directory.
3. Run:

```
Get-FileHash <filename> -Algorithm SHA256
```

4. Compare the hash output to the value listed in the README.

---

## Interpretation

* **Match:**
  The file has not been altered since delivery.

* **Mismatch:**
  The file has been modified or corrupted and should not be relied upon.

---

## Timestamp

Hashes were generated at the time of delivery and timestamped in UTC.
The timestamp is included in the README and recorded in the delivery log.

---

## Notes for Auditors and Reviewers

* Hashes are deterministic and independently reproducible.
* No proprietary tools or credentials are required.
* Verification does not rely on trust in the author.
* Verification can be repeated at any time.

If the hashes match, the artifacts are authentic.
If they do not, the artifacts should be treated as invalid.
