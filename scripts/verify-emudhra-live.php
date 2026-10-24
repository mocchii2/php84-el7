<?php
declare(strict_types=1);

$phase = $argv[1] ?? '';
if (!in_array($phase, ['before', 'after'], true)) {
    fwrite(STDERR, "Usage: php verify-emudhra-live.php before|after\n");
    exit(2);
}
$bundle = '/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt';
$hosts = [
    'repository.emsign.com' => true,
    'dv-g3b-emudhra.we-have-a-problem.com' => $phase === 'before',
    'dv-g3b-aaa-emudhra.we-have-a-problem.com' => $phase === 'before',
];

foreach ($hosts as $host => $expected) {
    $options = [
        'verify_peer' => true,
        'verify_peer_name' => true,
        'peer_name' => $host,
    ];
    if ($phase === 'before') {
        $options['cafile'] = $bundle;
    }
    $warnings = [];
    set_error_handler(static function (int $severity, string $message) use (&$warnings): bool {
        $warnings[] = $message;
        fwrite(STDERR, $message . "\n");
        return true;
    }, E_WARNING);
    try {
        $socket = stream_socket_client(
            "tls://$host:443",
            $errno,
            $errstr,
            15,
            STREAM_CLIENT_CONNECT,
            stream_context_create(['ssl' => $options]),
        );
    } finally {
        restore_error_handler();
    }
    $accepted = is_resource($socket);
    if ($accepted) {
        fclose($socket);
    }
    if ($accepted !== $expected) {
        throw new RuntimeException("Unexpected stream TLS result for $host: $errno $errstr");
    }
    if (!$accepted && !str_contains(implode("\n", $warnings), 'certificate verify failed')) {
        throw new RuntimeException("Not a certificate-verification rejection for $host");
    }
    echo "STREAM $phase $host: ", $accepted ? 'accepted' : 'rejected', "\n";

    $curl = curl_init("https://$host/");
    curl_setopt_array($curl, [
        CURLOPT_NOBODY => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_PROXY => '',
    ]);
    if ($phase === 'before') {
        curl_setopt($curl, CURLOPT_CAINFO, $bundle);
    }
    $response = curl_exec($curl);
    $error = curl_errno($curl);
    $message = curl_error($curl);
    curl_close($curl);
    if ($expected ? $response === false : $error !== CURLE_SSL_CACERT) {
        throw new RuntimeException("Unexpected cURL TLS result for $host: $error $message");
    }
    echo "CURL $phase $host: ", $response === false ? "rejected ($message)" : 'accepted', "\n";
}
