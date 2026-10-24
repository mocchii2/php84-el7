Name:           php84-pecl-imagick-muhoho
Version:        3.8.1
Release:        2%{?dist}
Summary:        Imagick extension for the muhoho PHP 8.4 stack
License:        PHP-3.01
URL:            https://pecl.php.net/package/imagick
Source0:        https://pecl.php.net/get/imagick-%{version}.tgz
Patch0:         imagick-3.8.1-similarity-test-imagemagick-2025.patch

BuildRequires:  php-devel = 8.4.27
BuildRequires:  devtoolset-12-gcc
BuildRequires:  imagemagick6-muhoho-devel >= 6.9.13.59
Requires:       php-common%{?_isa} = 8.4.27
Requires:       php(api) = 20240924-%{__isa_bits}
Requires:       php(zend-abi) = 20240924-%{__isa_bits}
Requires:       imagemagick6-muhoho%{?_isa} >= 6.9.13.59
Provides:       php-pecl-imagick = %{version}-%{release}
Obsoletes:      php-pecl-imagick < %{version}-%{release}
Provides:       php-pecl-imagick-im6 = %{version}-%{release}
Obsoletes:      php-pecl-imagick-im6 < %{version}-%{release}

%description
Imagick extension rebuilt for PHP 8.4 API 20240924 and the private
ImageMagick 6 Q16 runtime.

%prep
%setup -q -n imagick-%{version}
%patch0 -p1

%build
source /opt/rh/devtoolset-12/enable
phpize
export PKG_CONFIG_PATH=/opt/ImageMagick-6.9.13-59/lib64/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
export CPPFLAGS="-I/opt/ImageMagick-6.9.13-59/include/ImageMagick-6"
export CFLAGS="%{optflags}"
export LDFLAGS="-Wl,--enable-new-dtags -Wl,-rpath,/opt/ImageMagick-6.9.13-59/lib64 -L/opt/ImageMagick-6.9.13-59/lib64"
./configure --with-php-config=/usr/bin/php-config --with-imagick=/opt/ImageMagick-6.9.13-59
make -j6

%install
rm -rf %{buildroot}
install -Dpm0755 modules/imagick.so %{buildroot}%{_libdir}/php/modules/imagick.so
install -Dpm0644 /dev/null %{buildroot}%{_sysconfdir}/php.d/40-imagick.ini
echo 'extension=imagick.so' > %{buildroot}%{_sysconfdir}/php.d/40-imagick.ini

%check
make test NO_INTERACTION=1 REPORT_EXIT_STATUS=1 TESTS='--show-diff'
php -n -d extension=$PWD/modules/imagick.so -r '$i=new Imagick(); $i->newImage(32,24,"red"); $i->setImageFormat("png"); exit(strlen($i->getImagesBlob()) > 0 ? 0 : 1);'
ldd modules/imagick.so | grep -q '/opt/ImageMagick-6.9.13-59/lib64/libMagickWand-6.Q16.so.7'
! ldd modules/imagick.so | grep -Eq 'libssl\.so\.10|libcrypto\.so\.10'

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/php.d/40-imagick.ini
%{_libdir}/php/modules/imagick.so

%changelog
* Sat Oct 24 2026 Muhoho RPM build - 3.8.1-2
- Require matching PHP version and API/ABI without pinning its RPM release.

* Sat Oct 24 2026 Codex Build <root@localhost> - 3.8.1-1
- Rebuild Imagick for PHP 8.4 and private ImageMagick 6.
- Adjust only the similarity test boundaries for the ImageMagick 2025
  similarity calculation change tracked by Imagick upstream issue 737.
