Name:           libxslt-muhoho
Version:        1.1.45
Release:        1%{?dist}
Summary:        Private libxslt runtime for the muhoho PHP 8.4 stack
License:        MIT
URL:            https://gitlab.gnome.org/GNOME/libxslt
Source0:        https://download.gnome.org/sources/libxslt/1.1/libxslt-%{version}.tar.xz

BuildRequires:  devtoolset-12-gcc
BuildRequires:  make
BuildRequires:  pkgconfig
BuildRequires:  libxml2-muhoho-devel >= 2.15.4
BuildRequires:  libgcrypt-devel
Requires:       libxml2-muhoho%{?_isa} >= 2.15.4

%description
Private libxslt and libexslt for PHP 8.4, installed below
/opt/libxslt-1.1.45 without replacing the CentOS 7 system libraries.

%package devel
Summary:        Development files for the private libxslt runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libxml2-muhoho-devel%{?_isa} >= 2.15.4

%description devel
Headers and pkg-config metadata used to compile the private PHP stack.

%prep
%setup -q -n libxslt-%{version}

%build
source /opt/rh/devtoolset-12/enable
export PKG_CONFIG_PATH=/opt/libxml2-2.15.4/lib64/pkgconfig
export CPPFLAGS="-I/opt/libxml2-2.15.4/include/libxml2"
export CFLAGS="%{optflags} -fPIC"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/libxslt-1.1.45/lib64 -Wl,-rpath,/opt/libxml2-2.15.4/lib64 -L/opt/libxml2-2.15.4/lib64"
./configure \
    --prefix=/opt/libxslt-1.1.45 \
    --bindir=/opt/libxslt-1.1.45/bin \
    --includedir=/opt/libxslt-1.1.45/include \
    --libdir=/opt/libxslt-1.1.45/lib64 \
    --datadir=/opt/libxslt-1.1.45/share \
    --mandir=/opt/libxslt-1.1.45/share/man \
    --disable-static \
    --without-python
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/opt/libxslt-1.1.45/lib64/*.la

%check
make check
readelf -d %{buildroot}/opt/libxslt-1.1.45/bin/xsltproc | grep -q 'RUNPATH.*\[/opt/libxslt-1.1.45/lib64:/opt/libxml2-2.15.4/lib64\]'

%files
%license Copyright
%doc NEWS README.md
%dir /opt/libxslt-1.1.45
/opt/libxslt-1.1.45/bin
/opt/libxslt-1.1.45/lib64/libxslt.so.1*
/opt/libxslt-1.1.45/lib64/libexslt.so.0*
/opt/libxslt-1.1.45/share/man

%files devel
/opt/libxslt-1.1.45/include
/opt/libxslt-1.1.45/lib64/libxslt.so
/opt/libxslt-1.1.45/lib64/libexslt.so
/opt/libxslt-1.1.45/lib64/xsltConf.sh
/opt/libxslt-1.1.45/lib64/pkgconfig
/opt/libxslt-1.1.45/lib64/cmake
/opt/libxslt-1.1.45/share/doc
/opt/libxslt-1.1.45/share/gtk-doc

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 1.1.45-1
- Initial private EL7 package for PHP 8.4.
