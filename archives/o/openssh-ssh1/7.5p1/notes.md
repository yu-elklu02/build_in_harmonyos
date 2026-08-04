# openssh-ssh1 7.5p1

## Adaptation notes

- Uses the official OpenSSH portable 7.5p1 source archive.
- W0 dependencies are available in the `ohpcd` remote:
  - `zlib/1.3.1.1`
  - `openssl/1.1.1w`
- Applies small Autotools portability patches for OHOS:
  - accept `linux-ohos` host triplets in `config.sub`;
  - avoid `umask 077` temporary directories that fail on OHOS HMDFS.
- Disables platform integrations not available in the OpenHarmony environment:
  sandbox, utmp/utmpx, wtmp/wtmpx, and lastlog.
- Uses OpenSSL 1.1.1w because OpenSSH 7.5p1 directly accesses OpenSSL RSA,
  DSA, and EVP internals. OpenSSL 3.x makes those structures opaque and is not
  source-compatible with this SSH1-capable release without a large migration
  backport.

## Tests

- Upstream: `make tests`, covering the 14 default OpenSSH regression targets
  declared by `REGRESS_TARGETS` in `regress/Makefile`.
- Consumer: `test_package` checks the 7.5p1 version, runs `ssh -1 -G`, and
  creates an SSH1 RSA key pair with `ssh-keygen -t rsa1`.
