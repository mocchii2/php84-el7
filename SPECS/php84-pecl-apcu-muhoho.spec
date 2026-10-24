Name:           php84-pecl-apcu-muhoho
Version:        5.1.28
Release:        2%{?dist}
Summary:        APCu extension for the muhoho PHP 8.4 stack
License:        PHP-3.01
URL:            https://pecl.php.net/package/APCu
Source0:        https://pecl.php.net/get/apcu-%{version}.tgz

BuildRequires:  php-devel = 8.4.27
BuildRequires:  devtoolset-12-gcc
Requires:       php-common%{?_isa} = 8.4.27
Requires:       php(api) = 20240924-%{__isa_bits}
Requires:       php(zend-abi) = 20240924-%{__isa_bits}
Provides:       php-pecl-apcu = %{version}-%{release}
Obsoletes:      php-pecl-apcu < %{version}-%{release}

%description
APCu user data cache extension rebuilt for PHP 8.4 API 20240924.

%prep
%setup -q -n apcu-%{version}

%build
source /opt/rh/devtoolset-12/enable
phpize
export CFLAGS="%{optflags}"
./configure --with-php-config=/usr/bin/php-config --enable-apcu
make -j6

%install
rm -rf %{buildroot}
install -Dpm0755 modules/apcu.so %{buildroot}%{_libdir}/php/modules/apcu.so
install -Dpm0644 /dev/null %{buildroot}%{_sysconfdir}/php.d/40-apcu.ini
echo 'extension=apcu.so' > %{buildroot}%{_sysconfdir}/php.d/40-apcu.ini

%check
make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1 TESTS='--show-diff'
php -n -d extension=$PWD/modules/apcu.so -r 'exit(extension_loaded("apcu") ? 0 : 1);'

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/php.d/40-apcu.ini
%{_libdir}/php/modules/apcu.so

%changelog
* Sat Oct 24 2026 Muhoho RPM build - 5.1.28-2
- Require matching PHP version and API/ABI without pinning its RPM release.

* Sat Oct 24 2026 Codex Build <root@localhost> - 5.1.28-1
- Rebuild APCu for PHP 8.4 API 20240924.
