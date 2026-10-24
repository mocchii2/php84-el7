<?php
if (MeCab\version() !== '0.996') {
    throw new RuntimeException('unexpected MeCab version: ' . MeCab\version());
}

$text = 'すもももももももものうち';
$tagger = new MeCab\Tagger();
$parsed = $tagger->parse($text);
if (!is_string($parsed) || strpos($parsed, '名詞') === false) {
    throw new RuntimeException('parse() did not return expected Japanese features');
}

$parts = MeCab\split($text);
if (!is_array($parts) || count($parts) < 3 || implode('', $parts) !== $text) {
    throw new RuntimeException('split() round-trip failed');
}

$node = $tagger->parseToNode($text);
$surfaces = [];
foreach ($node as $item) {
    if ($item->getLength() > 0) {
        $surfaces[] = $item->getSurface();
    }
}
if (implode('', $surfaces) !== $text) {
    throw new RuntimeException('node iteration round-trip failed');
}

echo 'extension_version=' . phpversion('mecab') . PHP_EOL;
echo 'library_version=' . MeCab\version() . PHP_EOL;
echo 'morpheme_count=' . count($parts) . PHP_EOL;
echo 'node_count=' . count($surfaces) . PHP_EOL;
echo "result=PASS\n";
