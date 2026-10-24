<?php
declare(strict_types=1);

$payload = [
    'status' => 'ok',
    'count' => 3,
    'unicode' => '動作確認',
];
$options = ['encoding' => 'utf-8', 'escaping' => 'markup'];
$request = xmlrpc_encode_request('muhoho.health', [$payload], $options);
if (!str_contains($request, '<methodName>muhoho.health</methodName>')) {
    throw new RuntimeException('XML-RPC request encoding failed');
}

$method = null;
$decoded = xmlrpc_decode_request($request, $method, 'UTF-8');
if (getenv('XMLRPC_DIAG')) {
    echo $request, "\n";
    var_export([$method, $decoded]);
    echo "\n";
}
if ($method !== 'muhoho.health' || ($decoded[0] ?? null) !== $payload) {
    throw new RuntimeException('XML-RPC request roundtrip failed');
}

$response = xmlrpc_encode(['result' => true, 'message' => 'healthy']);
$responseDecoded = xmlrpc_decode($response, 'UTF-8');
if (($responseDecoded['result'] ?? null) !== true
    || ($responseDecoded['message'] ?? null) !== 'healthy') {
    throw new RuntimeException('XML-RPC value roundtrip failed');
}

echo "XML-RPC encode/decode UTF-8 roundtrip: PASS\n";
