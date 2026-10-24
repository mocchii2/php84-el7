Name:           php84-ca-policy-muhoho
Version:        20261024
Release:        1%{?dist}
Summary:        EL7 eMudhra distrust policy for the private PHP 8.4 stack
License:        Public Domain
BuildArch:      noarch
Source0:        emudhra-distrust-%{version}.tar.gz
BuildRequires:  openssl
Requires:       ca-certificates
Requires:       p11-kit-trust
Requires:       openssl35-muhoho >= 3.5.9
Requires:       libcurl-muhoho >= 8.23.0-2
Requires:       php-common >= 8.4
Requires(post): /usr/bin/update-ca-trust
Requires(postun): /usr/bin/update-ca-trust

%description
Blacklist the emSign ECC Root CA - G3 and sixteen affected intermediate
certificates (including cross-signatures) through EL7 update-ca-trust.
Keep AAA Certificate Services trusted for unrelated legitimate chains.
Connect private OpenSSL and PHP to the generated OpenSSL trust-policy
bundle, which preserves explicit rejection of intermediate certificates.
No generated system CA bundle is edited by this package.

%prep
%setup -q -n emudhra-distrust

%check
test "$(wc -l < certificates.sha256)" -eq 17
while read -r expected file; do
    actual=$(openssl x509 -in "$file" -outform DER | sha256sum | cut -d' ' -f1 | tr a-f A-F)
    test "$actual" = "$expected" || exit 1
done < certificates.sha256

%install
mkdir -p %{buildroot}/etc/pki/ca-trust/source/blacklist
while read -r expected file; do
    install -m 0644 "$file" "%{buildroot}/etc/pki/ca-trust/source/blacklist/muhoho-emudhra-$file"
done < certificates.sha256
mkdir -p %{buildroot}/opt/openssl35/ssl
ln -s /etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt \
    %{buildroot}/opt/openssl35/ssl/cert.pem
mkdir -p %{buildroot}/etc/php.d
cat > %{buildroot}/etc/php.d/zz-muhoho-ca-policy.ini <<'EOF'
openssl.cafile=/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt
curl.cainfo=/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt
EOF

%pre
if [ -e /opt/openssl35/ssl/cert.pem ] || [ -L /opt/openssl35/ssl/cert.pem ]; then
    if [ "$(readlink /opt/openssl35/ssl/cert.pem)" != /etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt ]; then
        echo "Refusing to replace existing private OpenSSL CA configuration" >&2
        exit 1
    fi
fi
if [ "$1" -eq 1 ]; then
    if [ -e /etc/php.d/zz-muhoho-ca-policy.ini ]; then
        echo "Refusing to replace existing PHP CA policy configuration" >&2
        exit 1
    fi
    for file in /etc/pki/ca-trust/source/blacklist/muhoho-emudhra-*.pem; do
        if [ -e "$file" ]; then
            echo "Refusing to replace existing blacklist file: $file" >&2
            exit 1
        fi
    done
fi

%post
/usr/bin/update-ca-trust extract

%postun
/usr/bin/update-ca-trust extract

%files
%doc certificates.sha256
%config(noreplace) /etc/pki/ca-trust/source/blacklist/muhoho-emudhra-*.pem
%config(noreplace) /etc/php.d/zz-muhoho-ca-policy.ini
/opt/openssl35/ssl/cert.pem

%changelog
* Sat Oct 24 2026 muhoho Build <root@localhost> - 20261024-1
- Pin and blacklist the affected root and sixteen intermediate certificates.
- Preserve intermediate rejection through the generated OpenSSL trust bundle.
