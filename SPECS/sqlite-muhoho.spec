Name:           sqlite-muhoho
Version:        3.54.1
Release:        1%{?dist}
Summary:        Private SQLite runtime for the muhoho PHP 8.4 stack
License:        Public Domain
URL:            https://sqlite.org/
Source0:        https://sqlite.org/2026/sqlite-autoconf-3540100.tar.gz

BuildRequires:  devtoolset-12-gcc
BuildRequires:  make
BuildRequires:  tcl-devel
BuildRequires:  zlib-muhoho-devel >= 1.3.2
Requires:       zlib-muhoho%{?_isa} >= 1.3.2

%description
Private SQLite for PHP 8.4, installed below /opt/sqlite-3.54.1 without
replacing the CentOS 7 system library or command-line program.

%package devel
Summary:        Development files for the private SQLite runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata used to compile the private PHP stack.

%prep
%setup -q -n sqlite-autoconf-3540100

%build
source /opt/rh/devtoolset-12/enable
export PKG_CONFIG_PATH=/opt/zlib-1.3.2/lib64/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
export CPPFLAGS="-I/opt/zlib-1.3.2/include"
export CFLAGS="%{optflags} -fPIC -DSQLITE_ENABLE_COLUMN_METADATA=1 -DSQLITE_ENABLE_FTS5=1 -DSQLITE_ENABLE_RTREE=1"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/sqlite-3.54.1/lib64 -Wl,-rpath,/opt/zlib-1.3.2/lib64 -L/opt/zlib-1.3.2/lib64"
./configure \
  --prefix=/opt/sqlite-3.54.1 \
  --libdir=/opt/sqlite-3.54.1/lib64 \
  --soname=legacy \
  --disable-static \
  --enable-shared
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
rm -f %{buildroot}/opt/sqlite-3.54.1/lib64/*.la

%check
test "$(./sqlite3 :memory: 'select sqlite_version();')" = "3.54.1"
test "$(./sqlite3 :memory: 'create table t(x); insert into t values(42); pragma integrity_check; select x from t;')" = $'ok\n42'
test "$(printf "%s\n" "create virtual table f using fts5(x); insert into f values('private sqlite works'); select count(*) from f where f match 'works';" | ./sqlite3 :memory:)" = "1"
test "$(printf "%s\n" "select json_valid('{}');" | ./sqlite3 :memory:)" = "1"
readelf -d %{buildroot}/opt/sqlite-3.54.1/lib64/libsqlite3.so.0 | grep -q 'RUNPATH.*\/opt\/zlib-1.3.2\/lib64'
readelf -d %{buildroot}/opt/sqlite-3.54.1/lib64/libsqlite3.so.0 | grep -q 'SONAME.*\[libsqlite3.so.0\]'

%files
%dir /opt/sqlite-3.54.1
/opt/sqlite-3.54.1/bin/sqlite3
/opt/sqlite-3.54.1/lib64/libsqlite3.so.0*
/opt/sqlite-3.54.1/lib64/libsqlite3.so.3.54.1
/opt/sqlite-3.54.1/share/man

%files devel
/opt/sqlite-3.54.1/include
/opt/sqlite-3.54.1/lib64/libsqlite3.so
/opt/sqlite-3.54.1/lib64/pkgconfig

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 3.54.1-1
- Initial private EL7 package for PHP 8.4.
