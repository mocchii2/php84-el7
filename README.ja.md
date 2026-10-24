# PHP 8.4.27 RPMs for EL7 (x86_64)

[English](README.md) | [日本語 / Japanese](README.ja.md)

> **緊急対応向け:** EL7環境でPHP 8.4系を迅速に検証・導入するための手順・ビルド設定集です。
> サポート対象OSへの移行までの暫定対応を想定しています。本番適用前に検証と復旧手段を確保してください。

> **For emergency use:** Procedures and build configurations for quickly testing and deploying PHP 8.4 on EL7.
> Intended as a temporary bridge to a supported OS. Validate your applications and establish a recovery plan before production use.

## このリポジトリでできること（3行） / What this repository does

EL7向けのPHP 8.4.27 / FPMと拡張を、署名付きRPMで導入できます。<br>
専用の依存ライブラリを使用し、OSのOpenSSLやnginxは置き換えません。<br>
完全な対応ソースRPM・SPEC・パッチから、自分でビルドできます。

Install PHP 8.4.27 / FPM and extensions on EL7 using signed RPMs.<br>
Use private dependency libraries without replacing system OpenSSL or nginx.<br>
Rebuild from complete corresponding source RPMs, SPECs and patches.

## 対応環境 / Target environment

- OS: EL7系 Linux（CentOS 7 / RHEL 7 / Oracle Linux 7）。
- アーキテクチャ: **x86_64のみ**。検証用ビルド環境はOracle Linux 7.9。
- nginx / PHP-FPM向け、NTSビルド。Apache mod_phpは提供しません。
- 全派生OSでの動作保証はありません。EL8/9、aarch64用ではありません。

- OS: EL7-family Linux (CentOS 7 / RHEL 7 / Oracle Linux 7).
- Architecture: **x86_64 only**. Build/test environment: Oracle Linux 7.9.
- NTS build for nginx / PHP-FPM; Apache mod_php is not provided.
- Not certified on every derivative/configuration. Not for EL8/9 or aarch64.

## 最短手順 / Quickstart: signature verification through installation

**以下はPHP未導入の新規・使い捨て検証ホスト向けです。**
既存PHPの移行は [INSTALL.md](INSTALL.md) に従い、クローンでリハーサルしてください。
本パッケージはシステムPHPを置き換えます。一発での本番更新には使わないでください。
スナップショットと復旧手順を確保し、信頼できるOSリポジトリから
`curl`、`gnupg2`、`tar`、`yum`、`sudo` を用意します。

必要なOS/EPEL依存（`capstone`、`nginx-filesystem`、`libmcrypt`など）は、
**署名検証が有効な信頼できるリポジトリから取得可能にするか、先に導入してください。**
EL7のアーカイブ設定は環境依存です。依存エラーを `--nodeps` や `--nogpgcheck` で
回避しないでください。nginx.org版を使っている場合も、依存を満たすためだけに
nginx本体を置き換えないでください。下記は開発用を含むRPM一式を選択しますが、
**任意のCAポリシーRPMは除外**します。

公開鍵の指紋は別の信頼できる経路でも確認してください。同じ配布元から取得した
鍵とファイルだけでは、配布元の身元を独立に確認したことにはなりません。

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
verification. The shared command block below applies to both languages.

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

FPM起動だけではWeb公開されません。nginx本体の導入・サイト設定・ソケット権限は
別途必要です。標準ソケットは `/var/run/php-fpm/php-fpm.sock` です。
失敗した場合はそこで止め、表示されたエラーを解決してから進めてください。
既存環境の設定や依存関係によって、上記以外の作業が必要です。

Starting FPM does not publish a website. Install/configure nginx, site routing
and socket permissions separately. The default socket is
`/var/run/php-fpm/php-fpm.sock`. Stop on errors and resolve them before
continuing; your existing configuration/dependencies may require extra work.
Run from an interactive terminal: yum reads its confirmation from `/dev/tty`.

## 注意点（既知の制約） / Known limitations

- **EL7はEOLです。** OS全体の安全性や、すべての脆弱性への対応を保証しません。
- 既存INIsの二重ロード、組み込み `sockets` の古いロード指定を確認してください。
- 既存FPMプール・セッション権限・アプリケーションの互換性は個別確認が必要です。
- MeCabは既存の `/etc/mecabrc` を使用します。配布辞書は上流IPADICだけです。
- CAポリシーは任意導入です。OS標準OpenSSLには既知の拒否制約があります。
- nginxのTLSは更新しません。詳細は [INSTALL.md](INSTALL.md)、
  [VALIDATION.md](VALIDATION.md)、[CA-POLICY.md](CA-POLICY.md) を参照してください。

- **EL7 is end-of-life.** This does not secure the entire OS or guarantee that
  every vulnerability is fixed.
- Check duplicate extension INIs and obsolete shared-load directives for the
  built-in `sockets` extension.
- Review existing FPM pools, session permissions and application compatibility.
- MeCab uses existing `/etc/mecabrc`; only upstream IPADIC is distributed.
- CA policy is opt-in; legacy system OpenSSL has documented distrust limitations.
- nginx TLS is not upgraded. See [INSTALL.md](INSTALL.md),
  [VALIDATION.md](VALIDATION.md) and [CA-POLICY.md](CA-POLICY.md).

## 動作確認ログ / Observed version output (2026-10-24)

EL7 x86_64の検証VMで取得した出力です。ビルド日時は配布済みバイナリのものです。

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
