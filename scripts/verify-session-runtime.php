<?php
declare(strict_types=1);

ini_set('session.save_handler', 'files');
ini_set('session.save_path', '/var/lib/php/session');
ini_set('session.use_cookies', '0');
ini_set('session.cache_limiter', '');
ini_set('session.gc_probability', '0');

$id = bin2hex(random_bytes(16));
session_id($id);
if (!session_start()) {
    throw new RuntimeException('Cannot create session');
}
$_SESSION['probe'] = $id;
if (!session_write_close()) {
    throw new RuntimeException('Cannot write session');
}
$_SESSION = [];
session_id($id);
if (!session_start() || ($_SESSION['probe'] ?? null) !== $id) {
    throw new RuntimeException('Cannot reuse session');
}
if (!session_destroy() || file_exists('/var/lib/php/session/sess_' . $id)) {
    throw new RuntimeException('Cannot destroy session');
}
echo "Session create/reuse/destroy: PASS\n";
