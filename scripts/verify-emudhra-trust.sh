#!/bin/bash
set -euo pipefail

if [[ $# -ne 2 || ! $1 =~ ^(before|after)$ ]]; then
    echo "Usage: $0 before|after PATH-TO-emudhra-distrust" >&2
    exit 2
fi
phase=$1
assets=$(cd "$2" && pwd)
private=/opt/openssl35/bin/openssl
bundle=/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt
work=$(mktemp -d)
trap 'rm -f "$work/result" "$work/roots.pem" "$work/aaa.pem" "$work/blacklist.pem"; rmdir "$work"' EXIT

echo "phase=$phase host=$(hostname) utc=$(date -u +%FT%TZ)"
rpm -q ca-certificates p11-kit-trust openssl35-muhoho libcurl-muhoho
php -r 'echo json_encode(openssl_get_cert_locations(), JSON_PRETTY_PRINT), "\n";
echo "curl_ssl=", curl_version()["ssl_version"], "\n";'
for path in /etc/pki/tls/cert.pem /etc/pki/tls/certs/ca-bundle.crt "$bundle" /opt/openssl35/ssl/cert.pem; do
    if [[ -e $path ]]; then
        echo "$path -> $(readlink -f "$path")"
        sha256sum "$path"
    else
        echo "ABSENT: $path"
    fi
done

count=0
while read -r expected file; do
    actual=$("$private" x509 -in "$assets/$file" -outform DER | sha256sum | cut -d' ' -f1 | tr a-f A-F)
    [[ $actual == "$expected" ]] || { echo "Fingerprint mismatch: $file" >&2; exit 1; }
    printf '%s %s\n' "$actual" "$file"
    count=$((count + 1))
done < "$assets/certificates.sha256"
[[ $count -eq 17 ]]
(cd "$assets/tls-chains" && sha256sum -c files.sha256)
for cert in "$assets"/EM-*-AAA.crt.pem; do
    original=${cert%-AAA.crt.pem}.crt.pem
    original_key=$("$private" x509 -in "$original" -pubkey -noout |
        "$private" pkey -pubin -outform DER | sha256sum | cut -d' ' -f1)
    cross_key=$("$private" x509 -in "$cert" -pubkey -noout |
        "$private" pkey -pubin -outform DER | sha256sum | cut -d' ' -f1)
    [[ $original_key == "$cross_key" ]]
    echo "SPKI MATCH: ${cert##*/} $cross_key"
done

# Verify a real retained anchor, not a fabricated replacement for the shared root.
"$private" crl2pkcs7 -nocrl -certfile /etc/pki/tls/certs/ca-bundle.crt |
    "$private" pkcs7 -print_certs > "$work/roots.pem"
awk 'BEGIN {RS="-----END CERTIFICATE-----"} /CN=AAA Certificate Services/ {
    start=index($0,"-----BEGIN CERTIFICATE-----");
    print substr($0,start) "-----END CERTIFICATE-----"
}' "$work/roots.pem" > "$work/aaa.pem"
[[ -s $work/aaa.pem ]]
"$private" x509 -in "$work/aaa.pem" -noout -subject -fingerprint -sha256
aaa_hash=$("$private" x509 -in "$work/aaa.pem" -outform DER | sha256sum | cut -d' ' -f1)
[[ $aaa_hash == d7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4 ]]
for openssl in /usr/bin/openssl "$private"; do
    "$openssl" verify -purpose sslserver -CAfile "$bundle" "$work/aaa.pem"
done
for openssl in "$private"; do
    if "$openssl" verify -purpose sslserver -CAfile "$bundle" \
        "$assets/emSignECCRootCAG3.pem" > "$work/result" 2>&1; then
        [[ $phase == before ]] || { echo "UNSAFE: emSign root accepted" >&2; exit 1; }
    else
        [[ $phase == after ]] || { cat "$work/result"; exit 1; }
        grep -q 'error 28 at .*depth lookup:.*certificate rejected' "$work/result" ||
            { cat "$work/result"; exit 1; }
    fi
done
php -r '$cert = file_get_contents($argv[1]);
if (openssl_x509_checkpurpose($cert, X509_PURPOSE_SSL_SERVER, [$argv[2]]) !== true) {
    throw new RuntimeException("Legitimate AAA root rejected");
}' "$work/aaa.pem" "$bundle"

for openssl in "$private"; do
    for chain in "$assets"/tls-chains/*.pem; do
        name=${chain##*/}
        name=${name%.pem}
        if "$openssl" verify -purpose sslserver -verify_hostname "$name" \
            -CAfile "$bundle" -untrusted "$chain" "$chain" > "$work/result" 2>&1; then
            [[ $phase == before ]] || { cat "$work/result"; echo "UNSAFE: $name accepted" >&2; exit 1; }
            echo "BASELINE ACCEPTED: $openssl $name"
        else
            cat "$work/result"
            [[ $phase == after ]] || { echo "Unexpected baseline failure: $name" >&2; exit 1; }
            grep -q 'error 28 at .*depth lookup:.*certificate rejected' "$work/result" ||
                { echo "Failure was not explicit distrust: $name" >&2; exit 1; }
            echo "DISTRUST CONFIRMED: $openssl $name"
        fi
        php -r '$chain=file_get_contents($argv[1]);
$expected=$argv[3] === "before" ? true : false;
$actual=openssl_x509_checkpurpose($chain, X509_PURPOSE_SSL_SERVER, [$argv[2]], $argv[1]);
if ($actual !== $expected) {
    throw new RuntimeException("Unexpected PHP chain result: " . var_export($actual, true));
}' "$chain" "$bundle" "$phase"
    done
done

if [[ $phase == after ]]; then
    trust extract --filter=blacklist --format=pem-bundle "$work/blacklist.pem"
    php -r 'preg_match_all("/-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----/s",
file_get_contents($argv[1]), $matches);
$actual = array_map(static fn(string $cert): string =>
    strtoupper(openssl_x509_fingerprint($cert, "sha256")), $matches[0]);
foreach (file($argv[2], FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
    [$expected, $name] = explode(" ", $line, 2);
    if (!in_array($expected, $actual, true)) {
        throw new RuntimeException("Missing extracted distrust certificate: " . $name);
    }
}
preg_match_all("/-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----/s",
file_get_contents($argv[3]), $anchors);
foreach ($anchors[0] as $cert) {
    if (strtoupper(openssl_x509_fingerprint($cert, "sha256")) ===
        "86A1ECBA089C4A8D3BBE2734C612BA341D813E043CF9E8A862CD5C57A36BBE6B") {
        throw new RuntimeException("Distrusted emSign root remains in OS anchor PEM");
    }
}
echo "All 17 pinned certificates blacklisted; emSign root absent from OS anchor PEM\n";' \
        "$work/blacklist.pem" "$assets/certificates.sha256" \
        /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
    [[ $(readlink -f /opt/openssl35/ssl/cert.pem) == "$bundle" ]]
    for env_name in SSL_CERT_FILE SSL_CERT_DIR CURL_CA_BUNDLE; do
        [[ -z ${!env_name:-} ]] || { echo "Unexpected CA environment override: $env_name" >&2; exit 1; }
    done
    php -r '$expected=$argv[1]; $locations=openssl_get_cert_locations();
if ($locations["ini_cafile"] !== $expected || ini_get("curl.cainfo") !== $expected) {
    throw new RuntimeException("PHP is not using the trust-policy bundle");
}' "$bundle"
    /opt/curl-8.23.0/bin/curl --version
fi
echo "PASS: $phase private OpenSSL/PHP trust-policy checks (not a legacy OS client certification)"
