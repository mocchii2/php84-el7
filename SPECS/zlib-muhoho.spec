Name:           zlib-muhoho
Version:        1.3.2
Release:        1%{?dist}
Summary:        Private zlib runtime for the muhoho PHP 8.4 stack
License:        Zlib
URL:            https://zlib.net/
Source0:        https://zlib.net/fossils/zlib-%{version}.tar.gz

BuildRequires:  devtoolset-12-gcc
BuildRequires:  make

%description
Private zlib for PHP 8.4, installed below /opt/zlib-1.3.2 without replacing
the CentOS 7 system library.

%package devel
Summary:        Development files for the private zlib runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata used to compile the private PHP stack.

%prep
%setup -q -n zlib-%{version}

%build
source /opt/rh/devtoolset-12/enable
export CFLAGS="%{optflags} -fPIC"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/zlib-1.3.2/lib64"
./configure --prefix=/opt/zlib-1.3.2 --libdir=/opt/zlib-1.3.2/lib64
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/opt/zlib-1.3.2/lib64/libz.a

%check
make test
readelf -d %{buildroot}/opt/zlib-1.3.2/lib64/libz.so.1.3.2 | grep -q 'RUNPATH.*\[/opt/zlib-1.3.2/lib64\]'

%files
%license LICENSE
%dir /opt/zlib-1.3.2
/opt/zlib-1.3.2/lib64/libz.so.1*

%files devel
/opt/zlib-1.3.2/include
/opt/zlib-1.3.2/lib64/libz.so
/opt/zlib-1.3.2/lib64/pkgconfig
/opt/zlib-1.3.2/share

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 1.3.2-1
- Initial private EL7 package for PHP 8.4.
