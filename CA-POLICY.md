# Optional eMudhra policy

`php84-ca-policy-muhoho` is opt-in. It blacklists `emSign ECC Root CA - G3`
and sixteen pinned affected intermediate/cross certificates using native
EL7 `/etc/pki/ca-trust/source/blacklist` and `update-ca-trust`.
It does not hand-edit generated stores or blanket-remove AAA Certificate Services.

Review the exact 17 fingerprints and public certificate assets in the
corresponding CA-policy SRPM. Do not equate inclusion of test chains with
automatic CRL checking. Official incident references used during preparation:

- https://bugzilla.mozilla.org/show_bug.cgi?id=2083449
- https://access.redhat.com/security/vulnerabilities/RHSB-2026-012

Check current official incident/revocation information before adopting policy;
the dated package is not a live revocation feed.

## Why the private bundle differs

Ordinary PEM anchor bundles cannot express intermediate rejection. The policy
sets the private OpenSSL `cert.pem` link and PHP openssl/cURL INI to:

```text
/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt
```

The private libcurl default also uses that generated OpenSSL trusted/rejected
bundle. The policy refuses to overwrite unexpected existing private CA
configuration. Inspect any customized overrides, environment variables and
explicit application CA bundles.

## Tests and limitation

The private OpenSSL/PHP stack rejected all 14 included synthetic chains and
the tested live direct/cross chains, while retaining AAA and normal TLS.
**Legacy OS OpenSSL 1.0.2 was still able to accept an affected cross chain**,
even with the enhanced store. This is not certified OS-wide protection.
nginx's separate TLS runtime is not upgraded by these packages.

The public source RPM contains only public certificate/chain assets and
fingerprint manifests, not signing keys. Verification helpers require the
extracted `emudhra-distrust` directory:

```sh
bash scripts/verify-emudhra-trust.sh after /path/to/emudhra-distrust
php scripts/verify-emudhra-live.php after
```

The live tests depend on external endpoint availability; inspect failures
rather than treating network errors as successful distrust.

## Rollback boundary

Back up prior trust sources, generated-bundle hashes, PHP overrides and private
CA links before installation. Review a normal yum removal of only the policy
RPM, inspect `.rpmsave`, run `update-ca-trust extract`, restore recorded local
overrides and restart affected consumers as authorized. Private libcurl still
defaults to the enhanced store after policy removal. Never remove unrelated
blacklists or anchors. Removing policy restores exposure and is not a
recommended routine operation.
