Name:           php84-pecl-xmlrpc-muhoho
Version:        1.0.0
Release:        0.5.RC3%{?dist}
Summary:        XML-RPC extension for the muhoho PHP 8.4 stack
License:        PHP-3.01
URL:            https://pecl.php.net/package/xmlrpc
Source0:        https://pecl.php.net/get/xmlrpc-1.0.0RC3.tgz
Patch0:         xmlrpc-php84-tests.patch

BuildRequires:  php-devel = 8.4.27
BuildRequires:  devtoolset-12-gcc
BuildRequires:  libxml2-muhoho-devel >= 2.15.4
Requires:       php-common%{?_isa} = 8.4.27
Requires:       php(api) = 20240924-%{__isa_bits}
Requires:       php(zend-abi) = 20240924-%{__isa_bits}
Requires:       php-xml%{?_isa} = 8.4.27
Requires:       libxml2-muhoho%{?_isa} >= 2.15.4
Provides:       php-pecl-xmlrpc = 1.0.0-0.3.RC3%{?dist}
Obsoletes:      php-pecl-xmlrpc < 1.0.0-0.3.RC3%{?dist}

%description
PECL XML-RPC extension rebuilt for PHP 8.4 API 20240924 and the private
libxml2 runtime.

%prep
%setup -q -n xmlrpc-1.0.0RC3
%patch0 -p1

%build
source /opt/rh/devtoolset-12/enable
phpize
export PKG_CONFIG_PATH=/opt/libxml2-2.15.4/lib64/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
export CPPFLAGS="-I/opt/libxml2-2.15.4/include/libxml2"
export CFLAGS="%{optflags}"
export LDFLAGS="-Wl,--enable-new-dtags -Wl,-rpath,/opt/libxml2-2.15.4/lib64 -L/opt/libxml2-2.15.4/lib64"
./configure --with-php-config=/usr/bin/php-config --with-xmlrpc
make -j6

%install
rm -rf %{buildroot}
install -Dpm0755 modules/xmlrpc.so %{buildroot}%{_libdir}/php/modules/xmlrpc.so
install -Dpm0644 /dev/null %{buildroot}%{_sysconfdir}/php.d/40-xmlrpc.ini
echo 'extension=xmlrpc.so' > %{buildroot}%{_sysconfdir}/php.d/40-xmlrpc.ini

%check
TEST_PHP_EXECUTABLE=/usr/bin/php REPORT_EXIT_STATUS=1 \
  php -n run-tests.php -n -q \
  -d extension=/usr/lib64/php/modules/xml.so \
  -d extension=$PWD/modules/xmlrpc.so tests
php -n -d extension=xml.so -d extension=$PWD/modules/xmlrpc.so -r 'exit(extension_loaded("xmlrpc") ? 0 : 1);'
ldd modules/xmlrpc.so | grep -q '/opt/libxml2-2.15.4/lib64/libxml2.so.16'

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/php.d/40-xmlrpc.ini
%{_libdir}/php/modules/xmlrpc.so

%changelog
* Sat Oct 24 2026 Muhoho RPM build - 1.0.0-0.5.RC3
- Load XML before XML-RPC explicitly so the regression tests really execute.
- Update two test fixtures for PHP 8.4 diagnostics without changing runtime code.

* Sat Oct 24 2026 Muhoho RPM build - 1.0.0-0.4.RC3
- Require matching PHP version and API/ABI without pinning its RPM release.

* Sat Oct 24 2026 Codex Build <root@localhost> - 1.0.0-0.3.RC3
- Rebuild XML-RPC for PHP 8.4 API 20240924.
