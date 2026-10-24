# Installation and migration review

This is a replacement system PHP stack. Do not run an unattended production
upgrade based only on these examples. Establish a maintenance window,
application acceptance checks and a **tested** recovery snapshot first.
Restoring a snapshot can discard newer database/reservation writes.

## Verify downloads

Obtain the PHP release assets and matching OpenSSL release assets. Confirm the
full release-key fingerprint from a trusted channel:

`F31EC32487D78F95819D941C6831939648F01B4C`

For each release, in separate directories:

```sh
mkdir -m 700 verify-keyring
gpg2 --homedir ./verify-keyring --import RPM-GPG-KEY-muhoho-php84
gpg2 --homedir ./verify-keyring --fingerprint
gpg2 --homedir ./verify-keyring --verify SHA256SUMS.asc SHA256SUMS
sha256sum -c SHA256SUMS
```

Download all manifest-listed files and verify before extracting tar archives.
After deliberately accepting the public key, `rpm --import` registers system
trust. `scripts/verify-deployment-rpms.sh DIRECTORY [ISOLATED-RPMDB]` checks
integrity, signatures and duplicate package names; it never installs RPMs.

## Capture your own baseline

Keep package inventory and original signed rollback RPMs, modules, effective
settings, `/etc/php*`, FPM unit/drop-ins, numeric session/cache permissions,
CA state and unmanaged extensions. Do not rely on `yum history undo` alone:
old repositories may no longer carry the required packages.

Retain a binary backup of any unmanaged MeCab extension for PHP rollback;
an 8.4 binary cannot load in 8.0. Exact old-version rollback is not guaranteed
when original RPMs are missing.

## Resolve and test offline

Obtain signed external dependencies (including `capstone`; `nginx-filesystem`
may be absent with nginx.org packaging). Inspect ownership/scriptlets and the
full dependency closure. Do not replace nginx just to satisfy this dependency.

The release includes `-devel` packages for reproducible build inputs; operators
may choose a smaller runtime set after resolving and testing its closure.
`php84-ca-policy-muhoho` is **opt-in**: exclude its RPM if you do not approve the
trust-policy change. Read CA-POLICY.md first.

Use a single staging directory with only the selected signed RPMs, including
the separate OpenSSL packages and required signed external dependencies.
Check `rpm -Kv` for all inputs. In a disposable clone, test a yum shell
transaction with repositories disabled and **both** options:

```text
--setopt=localpkg_gpgcheck=1 --setopt=tsflags=test
```

The old Apache `php` RPM is incompatible with this nginx/FPM-only candidate.
If installed, explicitly plan its removal in the same reviewed transaction.
Do not proceed on a host actually depending on mod_php. Preserve other packages.
A yum shell process may return zero despite dependency errors: inspect the
log and require successful resolution/transaction-test messages.

## Configuration traps

- Syntax-check existing php.ini before switching. A malformed section header
  can stop parsing. Do not copy a wholesale upstream default over local settings.
- `sockets` is built in; an old `extension=sockets` directive must not request
  a nonexistent shared module.
- Review old/new INI names for double loading (zip, mcrypt, XML-RPC in particular).
- Preserve customized `%config(noreplace)` settings; inspect `.rpmnew`/`.rpmsave`.
  Unmodified package defaults may legitimately be replaced.
- Preserve FPM pool users, sockets, socket modes and numeric session-directory
  ownership. Defaults use nginx and `/var/run/php-fpm/php-fpm.sock`.
- MeCab uses `/etc/mecabrc`; account for symlinks and user-dictionary availability.
  Do not replace existing dictionaries with bundled IPADIC without a deliberate
  application decision.
- Existing pools may intentionally have different session storage. Test each
  actual pool, not an assumed shared-session fixture.

Only after a successful clone rehearsal, stop FPM during the real reviewed
transaction, remove `tsflags=test`, validate config/links/modules and restart.
Validate normal and rejected TLS, each actual FPM pool, dictionary behavior,
and application acceptance without unintended writes.

## Rollback

Prefer a tested whole-system recovery plan with a current database backup.
RPM-only rollback needs exact old signed packages, configs, permissions and
unmanaged binary restoration. EL7 yum obsoletes can require two transactions:
remove new replacement extension names first, then downgrade/reinstall old
ones. Review dependency removals and stop FPM throughout.
Do not force file replacement, use `--nodeps`, or copy a PHP 8.0 extension
into the running 8.4 runtime.
