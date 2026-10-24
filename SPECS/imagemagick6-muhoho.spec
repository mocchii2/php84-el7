Name:           imagemagick6-muhoho
Version:        6.9.13.59
Release:        1%{?dist}
Summary:        Private ImageMagick 6 runtime for the muhoho PHP stack
License:        ImageMagick
URL:            https://imagemagick.org/
Source0:        https://download.imagemagick.org/archive/releases/ImageMagick-6.9.13-59.tar.xz

BuildRequires:  devtoolset-12-gcc
BuildRequires:  make
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  libwebp-devel
BuildRequires:  freetype-devel
BuildRequires:  bzip2-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-muhoho-devel >= 1.3.2
BuildRequires:  libxml2-muhoho-devel >= 2.15.4
Requires:       zlib-muhoho%{?_isa} >= 1.3.2
Requires:       libxml2-muhoho%{?_isa} >= 2.15.4

%description
Private ImageMagick 6 Q16 runtime used by the PHP Imagick extension. It is
installed below /opt/ImageMagick-6.9.13-59 and does not replace EL7 packages.

%package devel
Summary:        Development files for the private ImageMagick 6 runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for building the PHP Imagick extension.

%prep
%setup -q -n ImageMagick-6.9.13-59

%build
source /opt/rh/devtoolset-12/enable
export PKG_CONFIG_PATH=/opt/libxml2-2.15.4/lib64/pkgconfig:/opt/zlib-1.3.2/lib64/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}
export CPPFLAGS="-I/opt/libxml2-2.15.4/include/libxml2 -I/opt/zlib-1.3.2/include"
export CFLAGS="%{optflags} -fPIC"
export CXXFLAGS="%{optflags} -fPIC"
export LDFLAGS="-Wl,-z,relro -Wl,-z,now -Wl,--enable-new-dtags -Wl,-rpath,/opt/ImageMagick-6.9.13-59/lib64 -Wl,-rpath,/opt/libxml2-2.15.4/lib64 -Wl,-rpath,/opt/zlib-1.3.2/lib64 -L/opt/libxml2-2.15.4/lib64 -L/opt/zlib-1.3.2/lib64"
./configure \
  --prefix=/opt/ImageMagick-6.9.13-59 \
  --libdir=/opt/ImageMagick-6.9.13-59/lib64 \
  --disable-static --enable-shared \
  --with-quantum-depth=16 --disable-hdri \
  --without-perl --without-x --without-opencl \
  --with-modules=no --with-magick-plus-plus=no \
  --with-jpeg=yes --with-png=yes --with-tiff=yes --with-webp=yes \
  --with-freetype=yes --with-xml=yes --with-zlib=yes
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
find %{buildroot}/opt/ImageMagick-6.9.13-59 -name '*.la' -delete

%check
make check
MAGICK_CONFIGURE_PATH=$PWD/config MAGICK_CODER_MODULE_PATH='' \
  utilities/convert logo: -resize 64x64 /tmp/imagemagick6-muhoho-check.png
test "$(utilities/identify -format '%wx%h' /tmp/imagemagick6-muhoho-check.png)" = '64x48'
rm -f /tmp/imagemagick6-muhoho-check.png
test -f magick/.libs/libMagickCore-6.Q16.so
! ldd magick/.libs/libMagickCore-6.Q16.so | grep -Eq 'libssl\.so\.10|libcrypto\.so\.10'

%files
%license LICENSE NOTICE
%dir /opt/ImageMagick-6.9.13-59
/opt/ImageMagick-6.9.13-59/bin
/opt/ImageMagick-6.9.13-59/etc
/opt/ImageMagick-6.9.13-59/lib64/libMagickCore-6.Q16.so.*
/opt/ImageMagick-6.9.13-59/lib64/libMagickWand-6.Q16.so.*
/opt/ImageMagick-6.9.13-59/lib64/ImageMagick-6.9.13
/opt/ImageMagick-6.9.13-59/share

%files devel
/opt/ImageMagick-6.9.13-59/include
/opt/ImageMagick-6.9.13-59/lib64/libMagickCore-6.Q16.so
/opt/ImageMagick-6.9.13-59/lib64/libMagickWand-6.Q16.so
/opt/ImageMagick-6.9.13-59/lib64/pkgconfig

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 6.9.13.59-1
- Initial private ImageMagick 6 package for the PHP 8.4 stack.
