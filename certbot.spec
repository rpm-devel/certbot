%global certbot_ver 5.6.0
%global debug_package %{nil}

# -----------------------------------------------------------------------
# Python interpreter selection
#
# certbot 5.x requires Python >= 3.10.
#   EL7  : Python 3.10+ is NOT in standard repos — build will fail unless
#           python3.10+ is installed from a third-party repo (e.g. IUS).
#           EL7 is listed for completeness; skip that chroot in practice.
#   EL8  : python3.11 is in AppStream — set as the interpreter explicitly.
#   EL9+ : system python3 is 3.11+ — use it directly.
#   Fedora: system python3 is 3.12+ — fine.
# -----------------------------------------------------------------------
%if 0%{?rhel} && 0%{?rhel} <= 7
%{error: EL7 does not provide Python >= 3.10 — certbot 5.x cannot be built for EL7}
%endif

%if 0%{?rhel} && 0%{?rhel} <= 8
%global certbot_python  python3.11
%global certbot_pybin   /usr/bin/python3.11
%else
%global certbot_python  python3
%global certbot_pybin   %{__python3}
%endif

# Resolve the correct site-packages path for --prefix /usr.
# On EL8, python3.11 has a default prefix of /usr/local, so plain
# sysconfig.get_path('purelib') returns the wrong base.  Query with
# explicit base=/usr to match the pip --prefix /usr used in %%install.
%global certbot_sitelib %(%{certbot_pybin} -c "import sysconfig; print(sysconfig.get_path('purelib', vars={'base': '/usr', 'platbase': '/usr'}))" 2>/dev/null)

# -----------------------------------------------------------------------
# Source tarballs — certbot core, acme library, and all official plugins
# -----------------------------------------------------------------------
Name:           certbot
Version:        %{certbot_ver}
Release:        9%{?dist}
Summary:        EFF ACME client with all official plugins
License:        Apache-2.0
URL:            https://certbot.eff.org
Source0:  https://files.pythonhosted.org/packages/source/c/certbot/certbot-%{certbot_ver}.tar.gz
Source1:  https://files.pythonhosted.org/packages/source/a/acme/acme-%{certbot_ver}.tar.gz
Source2:  https://files.pythonhosted.org/packages/source/c/certbot-apache/certbot_apache-%{certbot_ver}.tar.gz
Source3:  https://files.pythonhosted.org/packages/source/c/certbot-nginx/certbot_nginx-%{certbot_ver}.tar.gz
Source4:  https://files.pythonhosted.org/packages/source/c/certbot-dns-cloudflare/certbot_dns_cloudflare-%{certbot_ver}.tar.gz
Source5:  https://files.pythonhosted.org/packages/source/c/certbot-dns-digitalocean/certbot_dns_digitalocean-%{certbot_ver}.tar.gz
Source6:  https://files.pythonhosted.org/packages/source/c/certbot-dns-dnsimple/certbot_dns_dnsimple-%{certbot_ver}.tar.gz
Source7:  https://files.pythonhosted.org/packages/source/c/certbot-dns-dnsmadeeasy/certbot_dns_dnsmadeeasy-%{certbot_ver}.tar.gz
Source8:  https://files.pythonhosted.org/packages/source/c/certbot-dns-gehirn/certbot_dns_gehirn-%{certbot_ver}.tar.gz
Source9:  https://files.pythonhosted.org/packages/source/c/certbot-dns-google/certbot_dns_google-%{certbot_ver}.tar.gz
Source10: https://files.pythonhosted.org/packages/source/c/certbot-dns-linode/certbot_dns_linode-%{certbot_ver}.tar.gz
Source11: https://files.pythonhosted.org/packages/source/c/certbot-dns-luadns/certbot_dns_luadns-%{certbot_ver}.tar.gz
Source12: https://files.pythonhosted.org/packages/source/c/certbot-dns-nsone/certbot_dns_nsone-%{certbot_ver}.tar.gz
Source13: https://files.pythonhosted.org/packages/source/c/certbot-dns-ovh/certbot_dns_ovh-%{certbot_ver}.tar.gz
Source14: https://files.pythonhosted.org/packages/source/c/certbot-dns-rfc2136/certbot_dns_rfc2136-%{certbot_ver}.tar.gz
Source15: https://files.pythonhosted.org/packages/source/c/certbot-dns-route53/certbot_dns_route53-%{certbot_ver}.tar.gz
Source16: https://files.pythonhosted.org/packages/source/c/certbot-dns-sakuracloud/certbot_dns_sakuracloud-%{certbot_ver}.tar.gz

# -----------------------------------------------------------------------
# Bundled setuptools wheel for EL8 — AppStream ships setuptools 65.5.0
# which rejects PEP 639 SPDX string license values used by certbot 5.x.
# setuptools >= 67.0 accepts them; 82.0.1 is the latest stable wheel.
# Always present so spectool downloads it regardless of build host.
# Only installed at build time on EL8 (see %%build).
# -----------------------------------------------------------------------
Source17: https://files.pythonhosted.org/packages/9d/76/f789f7a86709c6b087c5a2f52f911838cad707cc613162401badc665acfe/setuptools-82.0.1-py3-none-any.whl

# -----------------------------------------------------------------------
# Build dependencies
# -----------------------------------------------------------------------
BuildRequires: %{certbot_python}
BuildRequires: %{certbot_python}-pip
BuildRequires: %{certbot_python}-setuptools
BuildRequires: systemd-rpm-macros

# -----------------------------------------------------------------------
# Runtime — core deps available as system RPMs on EL8+/Fedora
# -----------------------------------------------------------------------
Requires: %{certbot_python}
Requires: %{certbot_python}-cryptography  >= 43.0.0
Requires: %{certbot_python}-pyOpenSSL     >= 25.0.0
Requires: %{certbot_python}-josepy        >= 2.0.0
Requires: %{certbot_python}-configobj     >= 5.0.6
Requires: %{certbot_python}-distro        >= 1.7.0
Requires: %{certbot_python}-parsedatetime >= 2.6
Requires: %{certbot_python}-pyparsing     >= 3.0.0
Requires: %{certbot_python}-requests
Requires: %{certbot_python}-dns           >= 2.6.1
Requires: %{certbot_python}-boto3         >= 1.20.34

# -----------------------------------------------------------------------
# Plugin-specific deps that may need to come from EPEL or PyPI:
#   DNS-Cloudflare   : python3-cloudflare >= 4.0
#   DNS-DigitalOcean : python3-digitalocean >= 1.15.0
#   DNS-Lexicon plugins (dnsimple, dnsmadeeasy, gehirn, linode, luadns,
#                        nsone, ovh, sakuracloud):
#                      python3-dns-lexicon >= 3.14.1
#   DNS-Google       : python3-google-api-python-client >= 1.6.5
#                      python3-google-auth >= 2.16.0
#   Apache plugin    : python3-augeas
# These are listed as Recommends so dnf pulls them automatically
# when the packages are available, but installation does not fail
# on systems where they are absent.
# -----------------------------------------------------------------------
%if 0%{?rhel} >= 8 || 0%{?fedora}
Recommends: %{certbot_python}-augeas
Recommends: %{certbot_python}-dns-lexicon >= 3.14.1
Recommends: %{certbot_python}-google-api-python-client >= 1.6.5
Recommends: %{certbot_python}-google-auth >= 2.16.0
%endif

# -----------------------------------------------------------------------
# Provides — virtual package names so other specs can depend on any
# of the former fragmented package names and still get resolved.
# -----------------------------------------------------------------------
Provides: certbot              = %{version}-%{release}
Provides: python3-certbot      = %{version}-%{release}
Provides: certbot-apache       = %{version}-%{release}
Provides: python3-certbot-apache = %{version}-%{release}
Provides: certbot-nginx        = %{version}-%{release}
Provides: python3-certbot-nginx = %{version}-%{release}
Provides: certbot-dns-cloudflare   = %{version}-%{release}
Provides: certbot-dns-digitalocean = %{version}-%{release}
Provides: certbot-dns-dnsimple     = %{version}-%{release}
Provides: certbot-dns-dnsmadeeasy  = %{version}-%{release}
Provides: certbot-dns-gehirn       = %{version}-%{release}
Provides: certbot-dns-google       = %{version}-%{release}
Provides: certbot-dns-linode       = %{version}-%{release}
Provides: certbot-dns-luadns       = %{version}-%{release}
Provides: certbot-dns-nsone        = %{version}-%{release}
Provides: certbot-dns-ovh          = %{version}-%{release}
Provides: certbot-dns-rfc2136      = %{version}-%{release}
Provides: certbot-dns-route53      = %{version}-%{release}
Provides: certbot-dns-sakuracloud  = %{version}-%{release}
Provides: python3-certbot-dns-cloudflare   = %{version}-%{release}
Provides: python3-certbot-dns-digitalocean = %{version}-%{release}
Provides: python3-certbot-dns-dnsimple     = %{version}-%{release}
Provides: python3-certbot-dns-dnsmadeeasy  = %{version}-%{release}
Provides: python3-certbot-dns-gehirn       = %{version}-%{release}
Provides: python3-certbot-dns-google       = %{version}-%{release}
Provides: python3-certbot-dns-linode       = %{version}-%{release}
Provides: python3-certbot-dns-luadns       = %{version}-%{release}
Provides: python3-certbot-dns-nsone        = %{version}-%{release}
Provides: python3-certbot-dns-ovh          = %{version}-%{release}
Provides: python3-certbot-dns-rfc2136      = %{version}-%{release}
Provides: python3-certbot-dns-route53      = %{version}-%{release}
Provides: python3-certbot-dns-sakuracloud  = %{version}-%{release}
Provides: python3-acme                     = %{version}-%{release}
Provides: acme                             = %{version}-%{release}

# -----------------------------------------------------------------------
# Obsoletes — replaces all pre-existing fragmented packages
# Version-bound so a future upstream reclaim of the name would not conflict
# -----------------------------------------------------------------------
Obsoletes: python3-certbot                     < %{version}-%{release}
Obsoletes: certbot-apache                      < %{version}-%{release}
Obsoletes: python3-certbot-apache              < %{version}-%{release}
Obsoletes: certbot-nginx                       < %{version}-%{release}
Obsoletes: python3-certbot-nginx               < %{version}-%{release}
Obsoletes: certbot-dns-cloudflare              < %{version}-%{release}
Obsoletes: certbot-dns-digitalocean            < %{version}-%{release}
Obsoletes: certbot-dns-dnsimple                < %{version}-%{release}
Obsoletes: certbot-dns-dnsmadeeasy             < %{version}-%{release}
Obsoletes: certbot-dns-gehirn                  < %{version}-%{release}
Obsoletes: certbot-dns-google                  < %{version}-%{release}
Obsoletes: certbot-dns-linode                  < %{version}-%{release}
Obsoletes: certbot-dns-luadns                  < %{version}-%{release}
Obsoletes: certbot-dns-nsone                   < %{version}-%{release}
Obsoletes: certbot-dns-ovh                     < %{version}-%{release}
Obsoletes: certbot-dns-rfc2136                 < %{version}-%{release}
Obsoletes: certbot-dns-route53                 < %{version}-%{release}
Obsoletes: certbot-dns-sakuracloud             < %{version}-%{release}
Obsoletes: python3-certbot-dns-cloudflare      < %{version}-%{release}
Obsoletes: python3-certbot-dns-digitalocean    < %{version}-%{release}
Obsoletes: python3-certbot-dns-dnsimple        < %{version}-%{release}
Obsoletes: python3-certbot-dns-dnsmadeeasy     < %{version}-%{release}
Obsoletes: python3-certbot-dns-gehirn          < %{version}-%{release}
Obsoletes: python3-certbot-dns-google          < %{version}-%{release}
Obsoletes: python3-certbot-dns-linode          < %{version}-%{release}
Obsoletes: python3-certbot-dns-luadns          < %{version}-%{release}
Obsoletes: python3-certbot-dns-nsone           < %{version}-%{release}
Obsoletes: python3-certbot-dns-ovh             < %{version}-%{release}
Obsoletes: python3-certbot-dns-rfc2136         < %{version}-%{release}
Obsoletes: python3-certbot-dns-route53         < %{version}-%{release}
Obsoletes: python3-certbot-dns-sakuracloud     < %{version}-%{release}
Obsoletes: python3-acme                        < %{version}-%{release}
Obsoletes: acme                                < %{version}-%{release}
Obsoletes: certbot-auto                        < %{version}-%{release}

%description
Certbot is the EFF's ACME client for automatically obtaining and renewing
TLS certificates from Let's Encrypt and any other ACME-compliant CA.

This package bundles certbot plus every official plugin in a single RPM:
  - certbot-apache   (Apache httpd integration)
  - certbot-nginx    (nginx integration)
  - certbot-dns-cloudflare, -digitalocean, -dnsimple, -dnsmadeeasy,
    -gehirn, -google, -linode, -luadns, -nsone, -ovh, -rfc2136,
    -route53, -sakuracloud   (DNS-01 challenge plugins)

It also obsoletes and replaces all individual certbot-* and
python3-certbot-* packages so a plain "dnf install certbot" is all
that is ever needed.

%prep
# Main certbot source becomes the working directory
%setup -q -n certbot-%{certbot_ver}

# Extract all other sources into _builddir side-by-side
cd %{_builddir}
for f in \
  %{SOURCE1}  %{SOURCE2}  %{SOURCE3}  %{SOURCE4}  \
  %{SOURCE5}  %{SOURCE6}  %{SOURCE7}  %{SOURCE8}  \
  %{SOURCE9}  %{SOURCE10} %{SOURCE11} %{SOURCE12} \
  %{SOURCE13} %{SOURCE14} %{SOURCE15} %{SOURCE16}; do
  tar xzf "$f"
done

%build
%if 0%{?rhel} && 0%{?rhel} <= 8
# EL8 AppStream ships setuptools 65.5.0, which rejects PEP 639 SPDX string
# license values (e.g. "Apache-2.0") used by certbot 5.x.  Upgrade to the
# bundled 82.0.1 wheel (Source17) before invoking pip wheel below.
%{certbot_pybin} -m pip install --quiet --no-index \
  --find-links %{_sourcedir} \
  --upgrade setuptools
%endif

# Build each package (setuptools backend, --no-build-isolation uses the
# system setuptools installed via BuildRequires)
install_order=(
  acme-%{certbot_ver}
  certbot-%{certbot_ver}
  certbot_apache-%{certbot_ver}
  certbot_nginx-%{certbot_ver}
  certbot_dns_cloudflare-%{certbot_ver}
  certbot_dns_digitalocean-%{certbot_ver}
  certbot_dns_dnsimple-%{certbot_ver}
  certbot_dns_dnsmadeeasy-%{certbot_ver}
  certbot_dns_gehirn-%{certbot_ver}
  certbot_dns_google-%{certbot_ver}
  certbot_dns_linode-%{certbot_ver}
  certbot_dns_luadns-%{certbot_ver}
  certbot_dns_nsone-%{certbot_ver}
  certbot_dns_ovh-%{certbot_ver}
  certbot_dns_rfc2136-%{certbot_ver}
  certbot_dns_route53-%{certbot_ver}
  certbot_dns_sakuracloud-%{certbot_ver}
)

for pkg_dir in "${install_order[@]}"; do
  pushd %{_builddir}/${pkg_dir}
  %{certbot_pybin} -m pip wheel --no-deps --no-build-isolation \
    --wheel-dir %{_builddir}/wheels .
  popd
done

%install
%{__rm} -rf %{buildroot}
# Install all built wheels into buildroot
for wheel in %{_builddir}/wheels/*.whl; do
  %{certbot_pybin} -m pip install \
    --no-deps \
    --no-build-isolation \
    --root    %{buildroot} \
    --prefix  %{_prefix} \
    "$wheel"
done

# Ensure the binary is executable
chmod 0755 %{buildroot}%{_bindir}/certbot

# Install renewal systemd timer and service
install -d %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/certbot-renew.service <<'UNIT'
[Unit]
Description=Certbot renewal
Documentation=https://certbot.eff.org/docs
[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew -q
PrivateTmp=true
UNIT

cat > %{buildroot}%{_unitdir}/certbot-renew.timer <<'UNIT'
[Unit]
Description=Twice-daily certbot renewal check
[Timer]
OnCalendar=*-*-* 00,12:00:00
RandomizedDelaySec=43200
Persistent=true
[Install]
WantedBy=timers.target
UNIT

%post
%systemd_post certbot-renew.service certbot-renew.timer

%preun
%systemd_preun certbot-renew.service certbot-renew.timer

%postun
%systemd_postun_with_restart certbot-renew.service certbot-renew.timer

%files
%license LICENSE.txt
%doc README.rst
%{_bindir}/certbot
%{certbot_sitelib}/certbot/
%{certbot_sitelib}/certbot-*.dist-info/
%{certbot_sitelib}/acme/
%{certbot_sitelib}/acme-*.dist-info/
%{certbot_sitelib}/certbot_apache/
%{certbot_sitelib}/certbot_apache-*.dist-info/
%{certbot_sitelib}/certbot_nginx/
%{certbot_sitelib}/certbot_nginx-*.dist-info/
%{certbot_sitelib}/certbot_dns_cloudflare/
%{certbot_sitelib}/certbot_dns_cloudflare-*.dist-info/
%{certbot_sitelib}/certbot_dns_digitalocean/
%{certbot_sitelib}/certbot_dns_digitalocean-*.dist-info/
%{certbot_sitelib}/certbot_dns_dnsimple/
%{certbot_sitelib}/certbot_dns_dnsimple-*.dist-info/
%{certbot_sitelib}/certbot_dns_dnsmadeeasy/
%{certbot_sitelib}/certbot_dns_dnsmadeeasy-*.dist-info/
%{certbot_sitelib}/certbot_dns_gehirn/
%{certbot_sitelib}/certbot_dns_gehirn-*.dist-info/
%{certbot_sitelib}/certbot_dns_google/
%{certbot_sitelib}/certbot_dns_google-*.dist-info/
%{certbot_sitelib}/certbot_dns_linode/
%{certbot_sitelib}/certbot_dns_linode-*.dist-info/
%{certbot_sitelib}/certbot_dns_luadns/
%{certbot_sitelib}/certbot_dns_luadns-*.dist-info/
%{certbot_sitelib}/certbot_dns_nsone/
%{certbot_sitelib}/certbot_dns_nsone-*.dist-info/
%{certbot_sitelib}/certbot_dns_ovh/
%{certbot_sitelib}/certbot_dns_ovh-*.dist-info/
%{certbot_sitelib}/certbot_dns_rfc2136/
%{certbot_sitelib}/certbot_dns_rfc2136-*.dist-info/
%{certbot_sitelib}/certbot_dns_route53/
%{certbot_sitelib}/certbot_dns_route53-*.dist-info/
%{certbot_sitelib}/certbot_dns_sakuracloud/
%{certbot_sitelib}/certbot_dns_sakuracloud-*.dist-info/
%{_unitdir}/certbot-renew.service
%{_unitdir}/certbot-renew.timer

%changelog
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-9
- Fix certbot_sitelib: pass base=/usr to sysconfig so the path matches
  pip --prefix /usr instead of python3.11's own default prefix (/usr/local)
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-8
- Fix %%files: use certbot_sitelib macro (resolved from interpreter) instead
  of %%{python3_sitelib} which points to python3.6 on EL8
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-7
- EL8: bundle setuptools-82.0.1 wheel (Source17); upgrade before %%build to
  fix PEP 639 SPDX string license rejection in AppStream setuptools 65.5.0
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-6
- Remove incorrect hatchling Sources/BuildRequires/%%build block — all
  certbot 5.6.0 packages use setuptools.build_meta, not hatchling
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-5
- EL8: bundle hatchling + deps (pathspec, pluggy, packaging, trove-classifiers)
  as wheel Sources (17-21); install offline via --no-index --find-links in
  %%build to avoid needing network access inside the mock chroot
- Use real hash-based PyPI URLs for reproducible spectool downloads
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-4
- EL8: drop python3.11-hatchling BuildRequires (not packaged); pip install
  hatchling at %%build time instead — %%no-build-isolation still satisfied
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-3
- Add version bounds to all Obsoletes (< version-release) to silence warnings
- Add %%global debug_package %%{nil} in spec so mock chroots suppress debuginfo
* Tue Jun  2 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-2
- Add EL7 error guard for Python 3.10+ requirement
- Add BuildRequires: systemd-rpm-macros
- Replace raw systemctl calls with systemd_post/preun/postun_with_restart macros
- Add %%postun section with systemd_postun_with_restart
- Add %%{__rm} -rf %%{buildroot} at top of %%install
- Fix bogus Thu weekday in changelog (May 22 2026 is Friday)
* Fri May 22 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 5.6.0-1
- Fix spec violations: remove BuildArch noarch, guard Recommends for EL7
* Fri May 22 2026 Jason Hempstead <git-admin@casjaysdev.pro> - 5.6.0-1
- Initial CasjaysDev bundled release
- Bundles certbot core, acme, apache, nginx, and all 13 DNS plugins
- Obsoletes all fragmented certbot-* and python3-certbot-* packages
