# Validation scope

The published RPMs are signed copies of the tested artifacts, not a promise of
compatibility with every legacy host.

- EL7 x86_64 build VM; PHP core/shared suite: 21,634 total, 18,816 passed,
  2,807 skipped, 10 expected failures, one warning; zero failures/timeouts/borked.
- Installed FPM suite: 122 passed, 15 skipped, one unexpected-pass warning,
  zero failures.
- Private libcurl suite: 1,647 reported OK, 2,138 considered. An initial run
  failed test 715; isolated retry passed. Final build used upstream six-worker,
  one-retry configuration, not a suppressed failure.
- NTS module retention, GD/imagick/IMAP/XML-RPC/MeCab/session checks, private
  library RUNPATH and absence of legacy OpenSSL links in PHP were tested.
- A signed offline PHP 8.0 -> 8.4 -> 8.0 rehearsal passed. Yum explicitly
  rejected an unsigned package with localpkg_gpgcheck enabled.
- Package header/content identity was compared before/after signing.
- RPM verification passed in an empty-then-minimal trust DB; repository and
  checksum signatures were verified using public-only keys.
- A production installation passed module, existing-config, two actual FPM
  pools, synthetic dictionary, TLS and safe nginx/FPM status checks. The
  operator subsequently reported successful application use.

Full production logs and private dictionaries are deliberately not published.
Tests on actual dictionaries used only synthetic inputs and compared digests;
that does not exhaustively test all dictionary entries or application flows.
No production-specific deployment/rollback script is offered as a generic tool.

The 58 baseline modules were retained, with 59 loaded after upgrade.
Pre-existing malformed INI, built-in sockets loading and duplicate extension
directives required targeted configuration corrections. Review INSTALL.md.

EL7 remains end-of-life. Tests establish observed behavior at release time,
not ongoing vulnerability coverage, FIPS approval, enterprise certification
or a working recovery snapshot for your host.

## Running the generic smoke checks

Use a disposable test VM, never an application entry point that may send mail
or write reservation data. The scripts fail explicitly on unmet requirements.

```sh
bash scripts/verify-php84-runtime.sh
php scripts/verify-gd-runtime.php /path/to/baseline-gd-info.json
php scripts/verify-imagick-runtime.php
php scripts/verify-xmlrpc-runtime.php
runuser -u nginx -- php scripts/verify-session-runtime.php
php -d mecab.default_rcfile=/dev/null \
  -d mecab.default_dicdir=/opt/mecab-0.996/lib64/mecab/dic/ipadic \
  scripts/verify-mecab-runtime.php
```

Capture the GD baseline on the old runtime **before** upgrading:

```sh
php -r 'echo json_encode(gd_info(), JSON_THROW_ON_ERROR), PHP_EOL;' > baseline-gd-info.json
```

For a fresh installation, a baseline captured on the current runtime exercises
the image operations but does not prove preservation of older GD capabilities.

The session probe creates/destroys its own random session under
`/var/lib/php/session`; it does not exercise your actual FPM pool settings.
The MeCab command deliberately selects the bundled IPADIC for a generic test;
it is not a recommendation to change an application's dictionary.
Image probes create temporary files and require their corresponding modules.
CA tests are described separately in CA-POLICY.md.
