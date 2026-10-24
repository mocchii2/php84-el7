Name:           php84-pecl-imap-muhoho
Version:        1.0.3
Release:        2%{?dist}
Summary:        IMAP extension for the muhoho PHP 8.4 stack
License:        PHP-3.01
URL:            https://pecl.php.net/package/imap
Source0:        https://pecl.php.net/get/imap-%{version}.tgz

BuildRequires:  php-devel = 8.4.27
BuildRequires:  devtoolset-12-gcc
BuildRequires:  openssl35-muhoho-devel >= 3.5.9
BuildRequires:  uw-imap-c-client-muhoho-devel = 2007f-1.el7
BuildRequires:  krb5-devel, pam-devel
Requires:       php-common%{?_isa} = 8.4.27
Requires:       php(api) = 20240924-%{__isa_bits}
Requires:       php(zend-abi) = 20240924-%{__isa_bits}
Requires:       openssl35-muhoho >= 3.5.9
Requires:       uw-imap-c-client-muhoho%{?_isa} = 2007f-1.el7
Provides:       php-imap = 8.4.27-1.muhoho.el7
Provides:       php-pecl-imap = %{version}-%{release}
Obsoletes:      php-imap < 8.4.27-1.muhoho.el7

%description
PECL IMAP extension rebuilt for PHP 8.4 API 20240924.  It links to the
private UW c-client and OpenSSL 3.5 libraries rather than CentOS 7 OpenSSL.

%prep
%setup -q -n imap-%{version}

%build
source /opt/rh/devtoolset-12/enable
phpize
export CPPFLAGS="-I/opt/openssl35/include"
export LDFLAGS="-Wl,--enable-new-dtags -Wl,-rpath,/opt/uw-imap-2007f/lib64 -Wl,-rpath,/opt/openssl35/lib64 -L/opt/uw-imap-2007f/lib64 -L/opt/openssl35/lib64"
export PKG_CONFIG_PATH="/opt/openssl35/lib64/pkgconfig"
./configure \
  --with-php-config=/usr/bin/php-config \
  --with-libdir=lib64 \
  --with-imap=/opt/uw-imap-2007f \
  --with-imap-ssl \
  --with-kerberos
make -j6

%install
rm -rf %{buildroot}
install -Dpm0755 modules/imap.so %{buildroot}%{_libdir}/php/modules/imap.so
install -Dpm0644 /dev/null %{buildroot}%{_sysconfdir}/php.d/20-imap.ini
echo 'extension=imap.so' > %{buildroot}%{_sysconfdir}/php.d/20-imap.ini

%check
make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1 TESTS='--show-diff'
php -n -d extension=$PWD/modules/imap.so -r 'exit(extension_loaded("imap") ? 0 : 1);'
readelf -d modules/imap.so | grep -F 'Shared library: [libc-client.so.2007f]'
readelf -d modules/imap.so | grep -F '/opt/uw-imap-2007f/lib64'
! readelf -d modules/imap.so | grep -E 'libssl\.so\.10|libcrypto\.so\.10'

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/php.d/20-imap.ini
%{_libdir}/php/modules/imap.so

%changelog
* Sat Oct 24 2026 Muhoho RPM build - 1.0.3-2
- Require matching PHP version and API/ABI without pinning its RPM release.

* Sat Oct 24 2026 Codex <root@localhost> - 1.0.3-1
- Build PECL IMAP for PHP 8.4 with private UW c-client and OpenSSL 3.5
