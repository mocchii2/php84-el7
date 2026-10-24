Name:           php84-mecab-muhoho
Version:        0.6.0
Release:        3.git89921c9%{?dist}
Summary:        MeCab extension for the muhoho PHP 8.4 stack
License:        MIT
URL:            https://github.com/rsky/php-mecab
Source0:        php-mecab-89921c991b0012f0e91c5ee8dd532f285cd172a4.tar.gz
Patch0:         php-mecab-php84-arginfo.patch
Patch1:         php-mecab-split-default-rcfile.patch
Patch2:         php-mecab-uninitialized-tagger.patch

BuildRequires:  php-devel = 8.4.27
BuildRequires:  devtoolset-12-gcc
BuildRequires:  mecab-muhoho-devel = 0.996-1%{?dist}
BuildRequires:  mecab-ipadic-muhoho = 2.7.0.20070801-1%{?dist}
Requires:       php-common%{?_isa} = 8.4.27
Requires:       php(api) = 20240924-%{__isa_bits}
Requires:       php(zend-abi) = 20240924-%{__isa_bits}
Requires:       mecab-muhoho%{?_isa} = 0.996-1%{?dist}
Provides:       php-mecab = %{version}-%{release}

%description
The php-mecab 0.6.0 API, using the reviewed PHP 8 compatibility commit from
upstream pull request 14 and linked to the private MeCab 0.996 runtime.

%prep
%setup -q -n php-mecab-89921c991b0012f0e91c5ee8dd532f285cd172a4
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
source /opt/rh/devtoolset-12/enable
cd mecab
phpize
export CFLAGS="%{optflags}"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/mecab-0.996/lib64 -L/opt/mecab-0.996/lib64"
./configure \
  --with-php-config=/usr/bin/php-config \
  --with-mecab=/opt/mecab-0.996/bin/mecab-config
make -j6

%install
rm -rf %{buildroot}
install -Dpm0755 mecab/modules/mecab.so %{buildroot}%{_libdir}/php/modules/mecab.so
install -Dpm0644 /dev/null %{buildroot}%{_sysconfdir}/php.d/20-mecab.ini
echo 'extension=mecab.so' > %{buildroot}%{_sysconfdir}/php.d/20-mecab.ini

%check
cd mecab
make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1 \
  TESTS='-d mecab.default_rcfile=/dev/null -d mecab.default_dicdir=/opt/mecab-0.996/lib64/mecab/dic/ipadic --show-diff'
php -n -d extension=$PWD/modules/mecab.so \
  -d mecab.default_rcfile=/dev/null \
  -d mecab.default_dicdir=/opt/mecab-0.996/lib64/mecab/dic/ipadic \
  -r '$t=new MeCab\Tagger(); $s=$t->parse("すもももももももものうち"); exit(strpos($s,"名詞") !== false ? 0 : 1);'
ldd modules/mecab.so | grep -q '/opt/mecab-0.996/lib64/libmecab.so.2'
! ldd modules/mecab.so | grep -Eq 'libssl\.so\.10|libcrypto\.so\.10'

%files
%license mecab/LICENSE
%doc README.md ChangeLog.md
%config(noreplace) %{_sysconfdir}/php.d/20-mecab.ini
%{_libdir}/php/modules/mecab.so

%changelog
* Sat Oct 24 2026 Muhoho RPM build - 0.6.0-3.git89921c9
- Reject calls on uninitialized taggers before reaching the native library.
- Test missing-configuration behavior without changing production defaults.

* Sat Oct 24 2026 Muhoho RPM build - 0.6.0-2.git89921c9
- Require matching PHP version and API/ABI without pinning its RPM release.

* Sat Oct 24 2026 Codex Build <root@localhost> - 0.6.0-1.git89921c9
- Port the existing production extension API to PHP 8.4 using upstream PR 14.
- Link only to the isolated MeCab 0.996 runtime.
- Add complete PHP 8.4 arginfo and iterator return types.
- Make MeCab\\split() honor mecab.default_rcfile consistently.
