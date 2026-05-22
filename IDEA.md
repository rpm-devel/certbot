# certbot — CasjaysDev bundled RPM

Single RPM that installs certbot and every official EFF plugin.
No `certbot-apache`, `certbot-nginx`, `python3-certbot-*`, or any
fragmented package name ever needed — just `dnf install certbot`.

## What is bundled

| Component | PyPI package |
|---|---|
| ACME library | `acme` |
| Core client | `certbot` |
| Apache plugin | `certbot-apache` |
| nginx plugin | `certbot-nginx` |
| Cloudflare DNS | `certbot-dns-cloudflare` |
| DigitalOcean DNS | `certbot-dns-digitalocean` |
| DNSimple DNS | `certbot-dns-dnsimple` |
| DNS Made Easy DNS | `certbot-dns-dnsmadeeasy` |
| Gehirn DNS | `certbot-dns-gehirn` |
| Google Cloud DNS | `certbot-dns-google` |
| Linode DNS | `certbot-dns-linode` |
| LuaDNS | `certbot-dns-luadns` |
| NS1 DNS | `certbot-dns-nsone` |
| OVH DNS | `certbot-dns-ovh` |
| RFC 2136 (DDNS) | `certbot-dns-rfc2136` |
| Route 53 DNS | `certbot-dns-route53` |
| Sakura Cloud DNS | `certbot-dns-sakuracloud` |

## Obsoletes / Provides

Every former fragmented package name is listed in both `Obsoletes:` and
`Provides:` so existing installs upgrade cleanly and other specs that
`Requires: python3-certbot` or any plugin name continue to resolve.

## Python version requirements

certbot 5.x requires Python >= 3.10.

| Platform | Python | Status |
|---|---|---|
| EL10 | 3.12 (system) | ✅ |
| EL9 | 3.11 (system) | ✅ |
| EL8 | 3.11 (AppStream) | ✅ — spec selects `python3.11` |
| EL7 | 3.6 (system) | ❌ — 3.10+ not in standard repos |
| Fedora 40+ | 3.12 (system) | ✅ |

## Auto-renewal

The RPM ships a systemd timer (`certbot-renew.timer`) that runs
`certbot renew -q` twice daily with a randomized delay. The timer is
enabled automatically on first install.

## Updating to a new certbot release

1. Update `%global certbot_ver` in `SPEC/certbot.spec`
2. Update the `Source:` URL hashes (PyPI embeds a content hash in the
   path — run `spectool --list-files SPEC/certbot.spec` after bumping
   the version to see which URLs need updating, or just let `spectool -g`
   resolve the new tarballs).
3. Update `%changelog`
4. `make srpm && make mock-el9`
