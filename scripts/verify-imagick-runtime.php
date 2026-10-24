<?php
$dir = sys_get_temp_dir() . '/imagick-muhoho-' . getmypid();
if (!mkdir($dir, 0700) && !is_dir($dir)) {
    throw new RuntimeException('temporary directory creation failed');
}

try {
    $image = new Imagick();
    $image->newImage(160, 120, new ImagickPixel('#336699'));
    $image->setImageFormat('png');
    $png = $image->getImagesBlob();
    if (strlen($png) < 100 || substr($png, 1, 3) !== 'PNG') {
        throw new RuntimeException('PNG blob validation failed');
    }
    $pngPath = $dir . '/source.png';
    if (file_put_contents($pngPath, $png) !== strlen($png)) {
        throw new RuntimeException('PNG write failed');
    }

    $roundTrip = new Imagick($pngPath);
    $roundTrip->thumbnailImage(80, 80, true);
    if ($roundTrip->getImageWidth() !== 80 || $roundTrip->getImageHeight() !== 60) {
        throw new RuntimeException('thumbnail geometry mismatch');
    }
    $roundTrip->setImageFormat('jpeg');
    $roundTrip->setImageCompressionQuality(82);
    $jpeg = $roundTrip->getImagesBlob();
    if (strlen($jpeg) < 100 || substr($jpeg, 0, 2) !== "\xff\xd8") {
        throw new RuntimeException('JPEG blob validation failed');
    }
    echo 'imagick_version=' . phpversion('imagick') . PHP_EOL;
    echo 'imagemagick_version=' . $roundTrip->getVersion()['versionString'] . PHP_EOL;
    echo 'png_bytes=' . strlen($png) . PHP_EOL;
    echo 'jpeg_bytes=' . strlen($jpeg) . PHP_EOL;
    echo 'thumbnail=80x60' . PHP_EOL;
    echo "result=PASS\n";
} finally {
    foreach (glob($dir . '/*') ?: [] as $path) {
        unlink($path);
    }
    rmdir($dir);
}
