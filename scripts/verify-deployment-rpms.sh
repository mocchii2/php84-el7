#!/bin/bash
set -euo pipefail
export LC_ALL=C

if [[ $# -lt 1 || $# -gt 2 || ! -d $1 ]]; then
    echo "Usage: $0 RPM-DIRECTORY [ISOLATED-RPM-DATABASE]" >&2
    exit 2
fi
rpm_command=(rpm)
if [[ $# -eq 2 ]]; then
    test -d "$2"
    rpm_command+=(--dbpath "$2")
fi
work=$(mktemp -d)
trap 'rm -f -- "$work/identities" "$work/check"; rmdir "$work"' EXIT
printf 'name\tnevra\tsignature_status\n'
count=0
unsigned=0
untrusted=0
shopt -s nullglob
for file in "$1"/*.rpm; do
    "${rpm_command[@]}" -K "$file" > "$work/check" 2>&1 || {
        cat "$work/check" >&2
        echo "RPM integrity/signature verification failed: $file" >&2
        exit 1
    }
    name=$("${rpm_command[@]}" -qp --qf '%{NAME}' "$file")
    nevra=$("${rpm_command[@]}" -qp --qf '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}' "$file")
    printf '%s\n' "$name" >> "$work/identities"
    signatures=$("${rpm_command[@]}" -qp --qf '%{SIGGPG:pgpsig}|%{SIGPGP:pgpsig}|%{RSAHEADER:pgpsig}|%{DSAHEADER:pgpsig}' "$file")
    if [[ "$signatures" == '(none)|(none)|(none)|(none)' ]]; then
        status=UNSIGNED
        unsigned=$((unsigned + 1))
    elif ! grep -Eqi '(gpg|pgp|rsa|dsa).*OK' "$work/check"; then
        status=SIGNATURE_NOT_CONFIRMED
        untrusted=$((untrusted + 1))
    else
        status=VERIFIED
    fi
    printf '%s\t%s\t%s\n' "$name" "$nevra" "$status"
    count=$((count + 1))
done
if [[ "$count" -eq 0 ]]; then
    echo "No RPMs found" >&2
    exit 1
fi
duplicates=$(sort "$work/identities" | uniq -d)
if [[ -n "$duplicates" ]]; then
    printf 'Duplicate package names:\n%s\n' "$duplicates" >&2
    exit 1
fi
printf 'RPMs=%s unsigned=%s signature_not_confirmed=%s\n' "$count" "$unsigned" "$untrusted" >&2
if [[ "$unsigned" -ne 0 || "$untrusted" -ne 0 ]]; then
    echo "BLOCKED: signature trust is not established for every RPM" >&2
    exit 1
fi
