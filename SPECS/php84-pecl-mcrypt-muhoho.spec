Name:           php84-pecl-mcrypt-muhoho
Version:        1.0.9
Release:        2%{?dist}
Summary:        mcrypt extension for the muhoho PHP 8.4 stack
License:        PHP-3.01
URL:            https://pecl.php.net/package/mcrypt
Source0:        https://pecl.php.net/get/mcrypt-%{version}.tgz

BuildRequires:  php-devel = 8.4.27
BuildRequires:  devtoolset-12-gcc
BuildRequires:  libmcrypt-devel
Requires:       php-common%{?_isa} = 8.4.27
Requires:       php(api) = 20240924-%{__isa_bits}
Requires:       php(zend-abi) = 20240924-%{__isa_bits}
Requires:       libmcrypt%{?_isa}
Provides:       php-pecl-mcrypt = %{version}-%{release}
Obsoletes:      php-pecl-mcrypt < %{version}-%{release}

%description
Legacy mcrypt extension rebuilt for PHP 8.4 API 20240924.

%prep
%setup -q -n mcrypt-%{version}

%build
source /opt/rh/devtoolset-12/enable
phpize
export CFLAGS="%{optflags}"
./configure --with-php-config=/usr/bin/php-config --with-mcrypt=/usr
make -j6

%install
rm -rf %{buildroot}
install -Dpm0755 modules/mcrypt.so %{buildroot}%{_libdir}/php/modules/mcrypt.so
install -Dpm0644 /dev/null %{buildroot}%{_sysconfdir}/php.d/40-mcrypt.ini
echo 'extension=mcrypt.so' > %{buildroot}%{_sysconfdir}/php.d/40-mcrypt.ini

%check
make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1 TESTS='--show-diff'
php -n -d extension=$PWD/modules/mcrypt.so -r 'exit(extension_loaded("mcrypt") ? 0 : 1);'

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/php.d/40-mcrypt.ini
%{_libdir}/php/modules/mcrypt.so

%changelog
* Sat Oct 24 2026 Muhoho RPM build - 1.0.9-2
- Require matching PHP version and API/ABI without pinning its RPM release.

* Sat Oct 24 2026 Codex Build <root@localhost> - 1.0.9-1
- Rebuild mcrypt for PHP 8.4 API 20240924.
