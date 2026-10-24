Name:           mecab-ipadic-muhoho
Version:        2.7.0.20070801
Release:        1%{?dist}
Summary:        Private UTF-8 IPA dictionary for MeCab
License:        mecab-ipadic
URL:            https://sourceforge.net/projects/mecab/files/mecab-ipadic/
Source0:        mecab-ipadic-2.7.0-20070801.tar.gz
BuildArch:      noarch

BuildRequires:  mecab-muhoho-devel = 0.996-1%{?dist}
Requires:       mecab-muhoho = 0.996-1%{?dist}

%description
UTF-8 IPA dictionary installed in the private MeCab 0.996 prefix.  It is
used for isolated functional validation and does not replace the production
NEologd dictionary or /etc/mecabrc.

%prep
%setup -q -n mecab-ipadic-2.7.0-20070801

%build
./configure \
  --prefix=/opt/mecab-0.996 \
  --with-mecab-config=/opt/mecab-0.996/bin/mecab-config \
  --with-charset=utf8
make -j6

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

%check
test -s %{buildroot}/opt/mecab-0.996/lib64/mecab/dic/ipadic/sys.dic
printf 'すもももももももものうち\n' | \
  /opt/mecab-0.996/bin/mecab -r /dev/null \
  -d %{buildroot}/opt/mecab-0.996/lib64/mecab/dic/ipadic | \
  grep -F 'すもも'

%files
%license COPYING
%doc AUTHORS README
/opt/mecab-0.996/lib64/mecab/dic/ipadic/

%changelog
* Sat Oct 24 2026 Codex Build <root@localhost> - 2.7.0.20070801-1
- Build the UTF-8 IPA dictionary for the isolated MeCab runtime.
