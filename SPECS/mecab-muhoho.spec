Name:           mecab-muhoho
Version:        0.996
Release:        1%{?dist}
Summary:        Private MeCab runtime for the muhoho PHP stack
License:        BSD or LGPLv2+ or GPL+
URL:            https://taku910.github.io/mecab/
Source0:        mecab-%{version}.tar.gz

BuildRequires:  devtoolset-12-gcc-c++

%description
MeCab 0.996 installed under /opt so it does not replace the CentOS system
library.  It uses the existing /etc/mecabrc by default to preserve the
production dictionary and user-dictionary configuration.

%package devel
Summary:        Development files for the private MeCab runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers, configuration helper, and linker files for building extensions
against the private MeCab runtime.

%prep
%setup -q -n mecab-%{version}

%build
source /opt/rh/devtoolset-12/enable
export CXXFLAGS="%{optflags} -std=gnu++14"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags"
./configure \
  --prefix=/opt/mecab-%{version} \
  --libdir=/opt/mecab-%{version}/lib64 \
  --sysconfdir=/etc \
  --with-charset=utf8 \
  --enable-shared \
  --disable-static
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
# Keep the compiled default path (/etc/mecabrc), but never own or replace the
# existing production configuration from this private runtime package.
rm -f %{buildroot}%{_sysconfdir}/mecabrc
find %{buildroot} -name '*.la' -delete

%check
make check
LD_LIBRARY_PATH=%{buildroot}/opt/mecab-%{version}/lib64 \
  %{buildroot}/opt/mecab-%{version}/bin/mecab --version | grep -Fx 'mecab of %{version}'
%{buildroot}/opt/mecab-%{version}/bin/mecab-config --version | grep -Fx '%{version}'

%files
%license BSD COPYING LGPL GPL
%doc AUTHORS README
/opt/mecab-%{version}/bin/mecab
/opt/mecab-%{version}/lib64/libmecab.so.2*
/opt/mecab-%{version}/libexec/mecab/
/opt/mecab-%{version}/share/man/man1/mecab.1*

%files devel
/opt/mecab-%{version}/bin/mecab-config
/opt/mecab-%{version}/include/mecab.h
/opt/mecab-%{version}/lib64/libmecab.so

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 0.996-1
- Package the production-compatible MeCab release in an isolated prefix.
- Preserve /etc/mecabrc as externally managed production configuration.
