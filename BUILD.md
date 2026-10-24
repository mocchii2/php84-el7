# Build from the complete source RPMs

Use an isolated EL7 x86_64 VM with sufficient memory/disk and an unprivileged
builder. Use the exact SRPMs from the release for the complete matching
sources, patches and templates; this Git repository intentionally does not
store large upstream tarballs.

Verify the release manifest/signature before extracting the sources archive.
`rpm -ivh SRPMS/package.src.rpm` installs source inputs in the builder's RPM
tree; it does not install the binary package.

Basic tools: `rpm-build`, `rpmdevtools`, `yum-utils`, `make`, `gcc`/`gcc-c++`
from SCL `devtoolset-12`, `gnupg2`, `cpio`, `tar`, `xz`, `bzip2`, `cmake3`,
`autoconf`, `automake`, `libtool`, and package-specific BuildRequires.
Many archived EL7/EPEL/SCL dependencies are required. Repository setup is
operator-specific: preserve vendor signature verification, never use `--nodeps`.

## Order

Install corresponding `-devel` binary results in the disposable build VM between
stages. Inspect each normal yum transaction. A practical dependency order is:

1. [OpenSSL 3.5.9](https://github.com/mocchii2/openssl35-el7), plus zlib and SQLite.
2. libxml2, libxslt, libcurl, libzip, ImageMagick.
3. MeCab runtime, upstream IPADIC, UW IMAP c-client.
4. PHP core and bundled/shared extensions.
5. PECL APCu/imagick/IMAP/mcrypt/XML-RPC and php-mecab.
6. Optional CA-policy package.

For each source RPM:

```sh
rpmdev-setuptree
rpm -ivh SRPMS/PACKAGE.src.rpm
source /opt/rh/devtoolset-12/enable
rpmbuild -ba "$HOME/rpmbuild/SPECS/PACKAGE.spec"
```

The PHP SPEC filename is `php84-muhoho.spec`, although its RPM name is `php`.
Its tested build is NTS, nginx/FPM, bundled GD; optional ZTS/Apache/other build
variants have not been certified here. Do not use `--nocheck` for a release.
Most private SPECs explicitly source `/opt/rh/devtoolset-12/enable`.
Some hard-code six workers, so size the VM accordingly.

`SPECS/` and `SOURCES/` preserve the recipes/patches/templates embedded in the
corresponding SRPMs. `source-inputs.sha256` records all source inputs extracted
from those SRPMs, including the upstream archives. Complete corresponding
source is distributed with the binaries rather than relying on source URLs
that may disappear.

No signing private key is provided. Use your own protected identity for
rebuilds. Matching sources do not imply bit-for-bit reproducibility.
