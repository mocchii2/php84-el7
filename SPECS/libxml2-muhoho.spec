Name:           libxml2-muhoho
Version:        2.15.4
Release:        1%{?dist}
Summary:        Private libxml2 runtime for the muhoho PHP 8.4 stack
License:        MIT
URL:            https://gitlab.gnome.org/GNOME/libxml2
Source0:        https://download.gnome.org/sources/libxml2/2.15/libxml2-%{version}.tar.xz

BuildRequires:  devtoolset-12-gcc
BuildRequires:  make
BuildRequires:  pkgconfig
BuildRequires:  zlib-devel
BuildRequires:  xz-devel
Requires:       zlib
Requires:       xz-libs

%description
Private libxml2 for PHP 8.4, installed below /opt/libxml2-2.15.4. It does
not replace the CentOS 7 system libxml2 used by system tools.

%package devel
Summary:        Development files for the private libxml2 runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       zlib-devel
Requires:       xz-devel

%description devel
Headers and pkg-config metadata used to compile the private PHP stack.

%prep
%setup -q -n libxml2-%{version}

%build
source /opt/rh/devtoolset-12/enable
export CFLAGS="%{optflags} -fPIC"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/libxml2-2.15.4/lib64"
./configure \
    --prefix=/opt/libxml2-2.15.4 \
    --bindir=/opt/libxml2-2.15.4/bin \
    --includedir=/opt/libxml2-2.15.4/include \
    --libdir=/opt/libxml2-2.15.4/lib64 \
    --datadir=/opt/libxml2-2.15.4/share \
    --mandir=/opt/libxml2-2.15.4/share/man \
    --disable-static \
    --with-zlib \
    --without-python
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/opt/libxml2-2.15.4/lib64/*.la

%check
make check
readelf -d %{buildroot}/opt/libxml2-2.15.4/bin/xmllint | grep -q 'RUNPATH.*\[/opt/libxml2-2.15.4/lib64\]'

%files
%license Copyright
%doc NEWS README.md
%dir /opt/libxml2-2.15.4
/opt/libxml2-2.15.4/bin
/opt/libxml2-2.15.4/lib64/libxml2.so.16*

%files devel
/opt/libxml2-2.15.4/include
/opt/libxml2-2.15.4/lib64/libxml2.so
/opt/libxml2-2.15.4/lib64/pkgconfig
/opt/libxml2-2.15.4/lib64/cmake

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 2.15.4-1
- Initial private EL7 package for PHP 8.4.
