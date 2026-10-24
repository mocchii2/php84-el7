Name:           libcurl-muhoho
Version:        8.23.0
Release:        2%{?dist}
Summary:        Private libcurl runtime for the muhoho PHP 8.4 stack
License:        curl
URL:            https://curl.se/
Source0:        https://curl.se/download/curl-%{version}.tar.xz

BuildRequires:  devtoolset-12-gcc
BuildRequires:  make
BuildRequires:  pkgconfig
BuildRequires:  openssl35-muhoho-devel >= 3.5.9
BuildRequires:  zlib-muhoho-devel >= 1.3.2
Requires:       openssl35-muhoho%{?_isa} >= 3.5.9
Requires:       zlib-muhoho%{?_isa} >= 1.3.2
Requires:       ca-certificates

%description
Private libcurl for PHP 8.4, installed below /opt/curl-8.23.0 without
replacing the CentOS 7 system curl or libcurl.

%package devel
Summary:        Development files for the private libcurl runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       openssl35-muhoho-devel%{?_isa} >= 3.5.9
Requires:       zlib-muhoho-devel%{?_isa} >= 1.3.2

%description devel
Headers and pkg-config metadata used to compile the private PHP stack.

%prep
%setup -q -n curl-%{version}

%build
source /opt/rh/devtoolset-12/enable
export PKG_CONFIG_PATH=/opt/openssl35/lib64/pkgconfig:/opt/zlib-1.3.2/lib64/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
export CPPFLAGS="-I/opt/openssl35/include -I/opt/zlib-1.3.2/include"
export CFLAGS="%{optflags} -fPIC"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/curl-8.23.0/lib64 -Wl,-rpath,/opt/openssl35/lib64 -Wl,-rpath,/opt/zlib-1.3.2/lib64 -L/opt/openssl35/lib64 -L/opt/zlib-1.3.2/lib64"
./configure \
  --prefix=/opt/curl-8.23.0 \
  --libdir=/opt/curl-8.23.0/lib64 \
  --disable-static \
  --enable-shared \
  --enable-ipv6 \
  --enable-threaded-resolver \
  --with-openssl=/opt/openssl35 \
  --with-ca-bundle=/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt \
  --without-ca-path \
  --with-zlib=/opt/zlib-1.3.2 \
  --without-libssh2 \
  --without-nghttp2 \
  --disable-ldap \
  --disable-ldaps \
  --without-libpsl \
  --without-brotli \
  --without-zstd \
  --without-libidn2 \
  --without-librtmp
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/opt/curl-8.23.0/lib64/*.la

%check
make test TFLAGS='-n -j6 --retry=1'
readelf -d %{buildroot}/opt/curl-8.23.0/lib64/libcurl.so.4 | grep -q 'RUNPATH.*\/opt\/curl-8.23.0\/lib64'

%files
%license COPYING
%doc README RELEASE-NOTES
%dir /opt/curl-8.23.0
/opt/curl-8.23.0/bin/curl
/opt/curl-8.23.0/bin/wcurl
/opt/curl-8.23.0/lib64/libcurl.so.4*
/opt/curl-8.23.0/share/man/man1/curl.1*
/opt/curl-8.23.0/share/man/man1/wcurl.1*

%files devel
/opt/curl-8.23.0/bin/curl-config
/opt/curl-8.23.0/share/man/man1/curl-config.1*
/opt/curl-8.23.0/include
/opt/curl-8.23.0/lib64/libcurl.so
/opt/curl-8.23.0/lib64/pkgconfig
/opt/curl-8.23.0/share/aclocal
/opt/curl-8.23.0/share/man/man3

%changelog
* Sat Oct 24 2026 muhoho Build <root@localhost> - 8.23.0-2
- Use the EL7 generated OpenSSL bundle to preserve intermediate CA rejection.
- Run the full upstream suite with six workers and one logged retry attempt.

* Sat Oct 24 2026 Codex Build <root@localhost> - 8.23.0-1
- Initial private EL7 package for PHP 8.4.
