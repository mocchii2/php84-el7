# PHP 8.4.27 RPMs for EL7 (x86_64)

> **Emergency use:** Test/deploy PHP 8.4 as a temporary bridge to a supported OS.<br>
> **Target:** EL7 x86_64, nginx/PHP-FPM (NTS); build/test environment: Oracle Linux 7.9.<br>
> **No warranty:** EL7 is EOL; no security or compatibility guarantee. Test first and prepare recovery.

[Installation / migration](INSTALL.md) | **[Rollback / recovery plan](INSTALL.md#rollback)**

[English](README.md) | [日本語 / Japanese](README.ja.md)

## What this repository does

Install PHP 8.4.27 / FPM and extensions on EL7 using signed RPMs.<br>
Use private dependency libraries without replacing system OpenSSL or nginx.<br>
Rebuild from complete corresponding source RPMs, SPECs and patches.

## Target environment

- OS: EL7-family Linux (CentOS 7 / RHEL 7 / Oracle Linux 7).
- Architecture: **x86_64 only**. Build/test environment: Oracle Linux 7.9.
- NTS build for nginx / PHP-FPM; Apache mod_php is not provided.
- Not certified on every derivative/configuration. Not for EL8/9 or aarch64.

## Quickstart: signature verification through installation

**The commands below are for a fresh, disposable test host without PHP.**
For an existing installation, follow [INSTALL.md](INSTALL.md) and rehearse on a
clone. These packages replace system PHP: this is not a one-shot production
upgrade. Have a recovery snapshot and restore procedure ready. Install `curl`,
`gnupg2`, `tar`, `yum` and `sudo` from trusted OS repositories first.

Required OS/EPEL dependencies (including `capstone`, `nginx-filesystem` and
`libmcrypt`) must be available from **trusted repositories with signature
verification enabled**, or installed beforehand. EL7 archive configuration
depends on your environment. Never bypass errors with `--nodeps` or
`--nogpgcheck`. Do not replace nginx.org's nginx just to satisfy a dependency.
This example selects the full package set, including development RPMs, but
**excludes the optional CA-policy RPM**.

Confirm the public-key fingerprint through an independent trusted channel.
Downloading a key and software from the same site is not independent identity
verification.

```sh
bash <<'BASH'
set -euo pipefail
if rpm -q php-common >/dev/null 2>&1 || command -v php >/dev/null 2>&1 ||
   command -v php-fpm >/dev/null 2>&1; then
  echo 'Existing PHP detected: stop and follow INSTALL.md for migration.' >&2
  exit 1
fi
if systemctl is-active --quiet php-fpm; then
  echo 'Existing FPM service detected: stop and review the migration plan.' >&2
  exit 1
fi
work=$(mktemp -d "$HOME/php84-el7.XXXXXX")
cd "$work"
for repo in openssl35-el7 php84-el7; do
  case "$repo" in
    openssl35-el7) tag=openssl-3.5.9-3.el7 ;;
    php84-el7) tag=php-8.4.27-3.muhoho.el7 ;;
  esac
  mkdir "$repo"
  (
    cd "$repo"
    base="https://github.com/mocchii2/$repo/releases/download/$tag"
    for file in "$repo-binary-rpms.tar.gz" "$repo-source-rpms.tar.gz" \
      PACKAGES.tsv source-inputs.sha256 RPM-GPG-KEY-muhoho-php84 SHA256SUMS SHA256SUMS.asc; do
      curl --fail --show-error --location --connect-timeout 20 --max-time 600 \
        --output "$file" "$base/$file"
    done
    mkdir -m 700 verify-keyring
    gpg2 --homedir "$PWD/verify-keyring" --batch --import RPM-GPG-KEY-muhoho-php84
    gpg2 --homedir "$PWD/verify-keyring" --batch --with-colons --fingerprint |
      grep -q '^fpr:::::::::F31EC32487D78F95819D941C6831939648F01B4C:'
    gpg2 --homedir "$PWD/verify-keyring" --batch --verify SHA256SUMS.asc SHA256SUMS
    sha256sum -c SHA256SUMS
    tar -xzf "$repo-binary-rpms.tar.gz"
  )
done
mkdir selected-rpms
cp openssl35-el7/RPMS/*.rpm selected-rpms/
for file in php84-el7/RPMS/*.rpm; do
  case "${file##*/}" in php84-ca-policy-muhoho-*) continue ;; esac
  cp "$file" selected-rpms/
done
sudo rpm --import php84-el7/RPM-GPG-KEY-muhoho-php84
rpm -Kv selected-rpms/*.rpm
sudo yum --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 \
  --setopt=tsflags=test localinstall selected-rpms/*.rpm </dev/tty
# Review the test transaction, then approve the real transaction at yum's prompt.
sudo yum --setopt=gpgcheck=1 --setopt=localpkg_gpgcheck=1 localinstall selected-rpms/*.rpm </dev/tty
php -v
sudo php-fpm -t
sudo systemctl enable --now php-fpm
sudo systemctl is-active php-fpm
printf 'Downloaded files retained in: %s\n' "$work"
BASH
```

Starting FPM does not publish a website. Install/configure nginx, site routing
and socket permissions separately. The default socket is
`/var/run/php-fpm/php-fpm.sock`. Stop on errors and resolve them before
continuing; your existing configuration/dependencies may require extra work.
Run from an interactive terminal: yum reads its confirmation from `/dev/tty`.

## Known limitations

- **EL7 is end-of-life.** This does not secure the entire OS or guarantee that
  every vulnerability is fixed.
- Check duplicate extension INIs and obsolete shared-load directives for the
  built-in `sockets` extension.
- Review existing FPM pools, session permissions and application compatibility.
- MeCab uses existing `/etc/mecabrc`; only upstream IPADIC is distributed.
- CA policy is opt-in; legacy system OpenSSL has documented distrust limitations.
- nginx TLS is not upgraded. See [INSTALL.md](INSTALL.md),
  [VALIDATION.md](VALIDATION.md) and [CA-POLICY.md](CA-POLICY.md).

## Observed version output (2026-10-24)

Captured on the EL7 x86_64 test VM. The build timestamp belongs to the
distributed binary, not the time these commands were run.

```console
$ php -v
PHP 8.4.27 (cli) (built: Oct 19 2026 14:38:59) (NTS gcc x86_64)
Copyright (c) The PHP Group
Zend Engine v4.4.27, Copyright (c) Zend Technologies
    with Zend OPcache v8.4.27, Copyright (c), by Zend Technologies

$ php -i | grep -E 'OpenSSL Library Version|cURL Information|libXML Compiled Version|SQLite Library'
cURL Information => 8.23.0
libXML Compiled Version => 2.15.4
OpenSSL Library Version => OpenSSL 3.5.9 29 Sep 2026
SQLite Library => 3.54.1
SQLite Library => 3.54.1
```

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
