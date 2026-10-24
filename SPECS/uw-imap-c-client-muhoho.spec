Name:           uw-imap-c-client-muhoho
Version:        2007f
Release:        1%{?dist}
Summary:        Private UW IMAP c-client library linked to OpenSSL 3.5
License:        Apache-2.0
URL:            https://github.com/uw-imap/imap
Source0:        imap-2007f.tar.gz
# Debian's maintained patch set; only the explicitly listed patches below are used.
Source1:        uw-imap_2007f_dfsg-7.debian.tar.xz

BuildRequires:  gcc, make, patch, xz
BuildRequires:  openssl35-muhoho-devel >= 3.5.9
BuildRequires:  pam-devel, krb5-devel
Requires:       openssl35-muhoho >= 3.5.9

%global imapprefix /opt/uw-imap-2007f

%description
Private, parallel-installable UW IMAP c-client build for the PHP 8.4 stack.
It uses the private OpenSSL 3.5 runtime and does not replace the CentOS 7
system c-client or OpenSSL packages.

%package devel
Summary:        Development files for the private UW IMAP c-client library
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and linker symlink for building the private PHP IMAP extension.

%prep
%setup -q -n imap-2007f
mkdir debian-patches
tar -xJf %{SOURCE1} -C debian-patches
for p in \
  1001_shlibs.patch \
  1002_flock_fix_syslog_args.patch \
  1003_fix_zero_len_when_mail_fetch_body_is_empty.patch \
  1005_poll.patch \
  1006_openssl1.1_autoverify.patch \
  2010_disallow_escaping_home.patch \
  2011_disable_version_check.patch \
  2013_disable_rsh.patch \
  2014_openssl1.1.1_sni.patch
do
  patch -p1 < "debian-patches/debian/patches/$p"
done

# Debian's shared-library patch expects an unset VERSION make variable.
# Give the private ABI a stable, explicit SONAME instead.
sed -i 's/libc-client\.so\.$(VERSION)/libc-client.so.2007f/' src/osdep/unix/Makefile

# Point the shared build at the parallel OpenSSL tree and embed its runtime path.
sed -i \
  's#GSSDIR=/usr SSLDIR=/usr SSLINCLUDE=/usr/include/openssl SSLCERTS=/etc/ssl/certs SSLKEYS=/etc/ssl/private#GSSDIR=/usr SSLDIR=/opt/openssl35 SSLINCLUDE=/opt/openssl35/include SSLLIB=/opt/openssl35/lib64 SSLCERTS=/etc/pki/tls/certs SSLKEYS=/etc/pki/tls/private EXTRALDFLAGS=-Wl,--enable-new-dtags,-rpath,/opt/openssl35/lib64#' \
  Makefile

%build
make ldbs IP6=4 SSLTYPE=unix.nopwd

%check
readelf -d c-client/libc-client.so | grep -F 'Library soname: [libc-client.so.2007f]'
readelf -d c-client/libc-client.so | grep -F 'Shared library: [libssl.so.3]'
readelf -d c-client/libc-client.so | grep -F 'Shared library: [libcrypto.so.3]'
readelf -d c-client/libc-client.so | grep -F '/opt/openssl35/lib64'
! readelf -d c-client/libc-client.so | grep -E 'libssl\.so\.10|libcrypto\.so\.10'

%install
rm -rf %{buildroot}
install -d %{buildroot}%{imapprefix}/lib64
install -m 0755 c-client/libc-client.so %{buildroot}%{imapprefix}/lib64/libc-client.so.2007f
ln -s libc-client.so.2007f %{buildroot}%{imapprefix}/lib64/libc-client.so

install -d %{buildroot}%{imapprefix}/include/c-client
for h in c-client/*.h; do
  install -m 0644 "$h" %{buildroot}%{imapprefix}/include/c-client/
done

%files
%{imapprefix}/lib64/libc-client.so.2007f

%files devel
%{imapprefix}/lib64/libc-client.so
%{imapprefix}/include/c-client/

%changelog
* Sat Oct 24 2026 Codex <root@localhost> - 2007f-1
- Build a private shared c-client against OpenSSL 3.5
- Apply Debian security, TLS hostname verification, and SNI patches
- Disable the legacy rsh transport
