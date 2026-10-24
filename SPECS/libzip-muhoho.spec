Name:           libzip-muhoho
Version:        1.12.1
Release:        1%{?dist}
Summary:        Private libzip runtime for the muhoho PHP 8.4 stack
License:        BSD-3-Clause
URL:            https://libzip.org/
Source0:        https://libzip.org/download/libzip-%{version}.tar.xz

BuildRequires:  devtoolset-12-gcc
BuildRequires:  cmake3
BuildRequires:  make
BuildRequires:  openssl35-muhoho-devel >= 3.5.9
BuildRequires:  zlib-muhoho-devel >= 1.3.2
BuildRequires:  bzip2-devel
BuildRequires:  xz-devel
BuildRequires:  libzstd-devel
Requires:       openssl35-muhoho%{?_isa} >= 3.5.9
Requires:       zlib-muhoho%{?_isa} >= 1.3.2

%description
Private libzip for PHP 8.4, installed below /opt/libzip-1.12.1 and linked
to the private OpenSSL 3.5 and zlib runtimes. It does not replace the EL7
system libzip package.

%package devel
Summary:        Development files for the private libzip runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and CMake/pkg-config metadata used to compile the private PHP stack.

%prep
%setup -q -n libzip-%{version}

%build
source /opt/rh/devtoolset-12/enable
export PKG_CONFIG_PATH=/opt/openssl35/lib64/pkgconfig:/opt/zlib-1.3.2/lib64/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
export CPPFLAGS="-I/opt/openssl35/include -I/opt/zlib-1.3.2/include"
export CFLAGS="%{optflags} -fPIC"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/libzip-1.12.1/lib64 -Wl,-rpath,/opt/openssl35/lib64 -Wl,-rpath,/opt/zlib-1.3.2/lib64 -L/opt/openssl35/lib64 -L/opt/zlib-1.3.2/lib64"
cmake3 -S . -B build \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_INSTALL_PREFIX=/opt/libzip-1.12.1 \
  -DCMAKE_INSTALL_LIBDIR=lib64 \
  -DCMAKE_INSTALL_RPATH='/opt/libzip-1.12.1/lib64;/opt/openssl35/lib64;/opt/zlib-1.3.2/lib64' \
  -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON \
  -DOPENSSL_ROOT_DIR=/opt/openssl35 \
  -DOPENSSL_USE_STATIC_LIBS=FALSE \
  -DZLIB_ROOT=/opt/zlib-1.3.2 \
  -DENABLE_OPENSSL=ON \
  -DENABLE_GNUTLS=OFF \
  -DBUILD_SHARED_LIBS=ON \
  -DBUILD_TOOLS=ON \
  -DBUILD_REGRESS=ON \
  -DBUILD_EXAMPLES=OFF \
  -DBUILD_DOC=OFF
cmake3 --build build --parallel 6

%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} cmake3 --install build
find %{buildroot}/opt/libzip-1.12.1 -name '*.a' -delete

%check
rm -f /tmp/libzip-muhoho-check.zip
build/src/ziptool -n /tmp/libzip-muhoho-check.zip add probe private-libzip
test "$(build/src/ziptool /tmp/libzip-muhoho-check.zip cat 0)" = "private-libzip"
build/src/ziptool -c /tmp/libzip-muhoho-check.zip stat 0 >/dev/null
rm -f /tmp/libzip-muhoho-check.zip
ldd build/lib/libzip.so | grep -q '/opt/openssl35/lib64/libcrypto.so.3'
! ldd build/lib/libzip.so | grep -Eq 'libcrypto\.so\.10|libssl\.so\.10'
readelf -d build/lib/libzip.so | grep -q 'RUNPATH.*\/opt\/openssl35\/lib64'

%files
%license LICENSE
%dir /opt/libzip-1.12.1
/opt/libzip-1.12.1/bin
/opt/libzip-1.12.1/lib64/libzip.so.*

%files devel
/opt/libzip-1.12.1/include
/opt/libzip-1.12.1/lib64/libzip.so
/opt/libzip-1.12.1/lib64/pkgconfig
/opt/libzip-1.12.1/lib64/cmake

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 1.12.1-1
- Initial private EL7 package for PHP 8.4.
