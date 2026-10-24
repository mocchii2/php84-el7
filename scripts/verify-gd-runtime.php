<?php
declare(strict_types=1);

if ($argc !== 2) {
    throw new InvalidArgumentException('Usage: php verify-gd-runtime.php baseline-gd-info.json');
}
$baselineJson = file_get_contents($argv[1]);
if ($baselineJson === false) {
    throw new RuntimeException('Cannot read GD feature baseline');
}
$baseline = json_decode($baselineJson, true, 512, JSON_THROW_ON_ERROR);
if (!is_array($baseline)) {
    throw new RuntimeException('Invalid GD feature baseline');
}
$current = gd_info();
foreach ($baseline as $feature => $supported) {
    if ($supported === true && ($current[$feature] ?? false) !== true) {
        throw new RuntimeException("Previously supported GD feature is missing: $feature");
    }
}

$image = imagecreatetruecolor(32, 48);
if ($image === false) {
    throw new RuntimeException('Cannot create GD image');
}
$color = imagecolorallocate($image, 64, 128, 192);
if ($color === false || !imagefill($image, 0, 0, $color)) {
    throw new RuntimeException('Cannot fill GD image');
}
foreach ([IMG_BICUBIC, IMG_BICUBIC_FIXED, IMG_BILINEAR_FIXED] as $method) {
    $scaled = imagescale($image, 64, -1, $method);
    if ($scaled === false || imagesx($scaled) !== 64 || imagesy($scaled) !== 96) {
        throw new RuntimeException("GD scaling/aspect-ratio regression for interpolation $method");
    }
}
foreach (['PNG' => 'imagepng', 'JPEG' => 'imagejpeg', 'WebP' => 'imagewebp'] as $format => $encode) {
    ob_start();
    try {
        if (!$encode($image)) {
            throw new RuntimeException("Cannot encode $format");
        }
        $data = ob_get_contents();
    } finally {
        ob_end_clean();
    }
    if ($data === false || $data === '') {
        throw new RuntimeException("Empty $format output");
    }
    $decoded = imagecreatefromstring($data);
    if ($decoded === false || imagesx($decoded) !== 32 || imagesy($decoded) !== 48) {
        throw new RuntimeException("Cannot roundtrip $format");
    }
}
echo 'GD version: ', $current['GD Version'], "\n";
echo "Previously supported GD features: preserved\n";
echo "Bicubic/bilinear scaling and aspect ratio: PASS\n";
echo "PNG/JPEG/WebP encode/decode: PASS\n";
