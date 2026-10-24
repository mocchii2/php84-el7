# License and source provenance

There is no single license for all bundled third-party software. Preserve the
upstream notices and consult each complete SRPM/archive for definitive terms.
The release ships complete corresponding source RPMs alongside binary RPMs.

| Component | Declared upstream/package license |
|---|---|
| PHP | PHP-3.01, Zend-2.0, BSD-2-Clause, MIT, Apache-1.0, NCSA, BSL-1.0 |
| OpenSSL (separate repository) | Apache-2.0 |
| zlib | Zlib |
| curl | curl license |
| libxml2, libxslt | MIT |
| libzip | BSD-3-Clause |
| SQLite | Public Domain |
| ImageMagick | ImageMagick license; retain LICENSE/NOTICE |
| MeCab | BSD or LGPLv2+ or GPL+; retain all included terms |
| IPADIC | Upstream mecab-ipadic terms in COPYING, not assumed MIT |
| php-mecab | MIT |
| APCu, imagick, PHP IMAP/mcrypt/XML-RPC extensions | PHP-3.01 as declared; inspect bundled notices |
| UW IMAP c-client | Apache-2.0 and bundled notices/patch attribution |
| CA-policy packaging | Public Domain declaration; public certificate test data retains provenance |

The large PHP SPEC derives from Fedora/Remi packaging with its original MIT
header and historical changelog retained. Upstream patch copyright/license
notices are not removed. Changes for private dependencies, test adaptation,
module compatibility and nginx-oriented packaging are visible in the recipes
and patches; this is not an upstream unmodified release.

New repository documentation and small helper scripts are MIT under LICENSE.
That grant does not supersede any third-party conditions or imply ownership of
upstream code. Complete source and applicable license/notice files remain in
each corresponding SRPM. Runtime RPMs retain license files; development
subpackages require the corresponding runtime.

EPEL capstone/nginx-filesystem and OS/compiler dependencies are not redistributed
here. Obtain them from a trusted vendor archive with their own licenses/signatures.
No production dictionary, site configuration, private signing key or credential
is included.
