# PHP 8.4.27 RPMs for EL7 (x86_64)

Unofficial community packaging for people maintaining legacy EL7 systems.
**EL7 is end-of-life. Prefer migrating to a supported OS.** These RPMs are
not a promise that all PHP, dependency or OS vulnerabilities are fixed.

## Components

- PHP/FPM **8.4.27**, release `3.muhoho.el7`.
- Bundled GD; private curl, XML/XSLT, SQLite, zip, zlib and ImageMagick libraries.
- APCu, imagick, IMAP, mcrypt, XML-RPC and MeCab extensions.
- Separately distributed [OpenSSL 3.5.9](https://github.com/mocchii2/openssl35-el7)
  under `/opt/openssl35`; system OpenSSL, curl and nginx are not replaced.
- Optional eMudhra CA-policy RPM using EL7 blacklist/update-ca-trust.

This is an nginx/FPM-oriented build: it does **not** provide Apache mod_php.
It replaces `/usr/bin/php`, PHP-FPM and PHP extension RPMs, not an SCL PHP
installation. Package names retain `muhoho` to match the tested artifacts.

## Downloads

[Releases](https://github.com/mocchii2/php84-el7/releases) contain **42 custom
binary RPMs and 18 complete corresponding source RPMs**, separate archives,
a signed checksum manifest and a public release key.
OpenSSL's two binary RPMs and one SRPM are published in the separate repository.
External EPEL dependencies such as `capstone` and `nginx-filesystem` must be
obtained from trusted vendor archives; they are not bundled here.

Read [INSTALL.md](INSTALL.md), [BUILD.md](BUILD.md),
[LICENSES.md](LICENSES.md) and [VALIDATION.md](VALIDATION.md).

Release public-key fingerprint:

```text
F31E C324 87D7 8F95 819D 941C 6831 9396 48F0 1B4C
```

The community signature authenticates the release, not upstream endorsement.
Verify this fingerprint through a trusted channel. Never disable GPG checks.

## Important limitations

- Existing INIs/pools require review. New package defaults do not establish
  safe behavior for arbitrary production configurations.
- `sockets` is built in; remove old shared-extension loading directives.
  Retained old/new INIs can double-load zip, mcrypt or XML-RPC.
- MeCab uses existing `/etc/mecabrc`; private packages do not overwrite it.
  Only the upstream IPADIC dictionary is distributed. No production NEologd,
  personal/user dictionary or site data is included.
- nginx TLS is independent; installing private OpenSSL does not add nginx TLS 1.3.
- The private CA policy enforces intermediate rejection in the private stack,
  **not all legacy OS OpenSSL consumers**. See [CA-POLICY.md](CA-POLICY.md).
- This repository does not include private deployment scripts, production
  backups/logs/configurations, signing secrets or credential files.

## License

Upstream code, patches and templates retain their original licenses and
copyright notices. New repository helpers/docs are MIT; there is no blanket
relicensing of the mixed-license source collection. See LICENSES.md.
