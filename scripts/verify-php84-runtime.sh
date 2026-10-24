#!/bin/bash
set -euo pipefail

echo '== Version =='
php -v

echo '== Library versions reported by PHP =='
php -i | egrep 'OpenSSL Library Version|cURL Information|libXML Compiled Version|SQLite Library'

echo '== FPM configuration =='
php-fpm -t

echo '== Direct binary links =='
ldd /usr/bin/php /usr/sbin/php-fpm | egrep '(^/|libssl|libcrypto|libxml2|libxslt|libcurl|libsqlite3|libz\.so)'

echo '== Old OpenSSL references =='
old_ssl_found=0
for file in /usr/bin/php /usr/sbin/php-fpm /usr/lib64/php/modules/*.so; do
    links=$(ldd "$file")
    if grep -Eq 'libssl\.so\.10|libcrypto\.so\.10|not found' <<< "$links"; then
        echo "BAD $file"
        echo "$links"
        old_ssl_found=1
    fi
done
echo "old_ssl_found=$old_ssl_found"

echo '== Private library RUNPATHs =='
readelf -d /usr/bin/php /usr/sbin/php-fpm \
    /usr/lib64/php/modules/curl.so \
    /usr/lib64/php/modules/mysqli.so \
    /usr/lib64/php/modules/pdo_mysql.so \
    /usr/lib64/php/modules/pdo_sqlite.so \
    /usr/lib64/php/modules/sqlite3.so \
    /usr/lib64/php/modules/xml.so \
    /usr/lib64/php/modules/xsl.so \
    | egrep 'File:|RPATH|RUNPATH'

exit "$old_ssl_found"
